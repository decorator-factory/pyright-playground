import base64
import gzip
import io
import zlib
from dataclasses import dataclass
from typing import Union

import httpx

from backend.github import download_gist_file
from backend.simple_error import Maybe, SimpleError


@dataclass(frozen=True)
class FromGzip:
    encoded: str


@dataclass(frozen=True)
class FromGist:
    gist_id: str
    filename: str


CodeSource = Union[FromGzip, FromGist]


HTTP_NOT_FOUND = 404
MAX_GZIP_SIZE_IN_BYTES = 65536


async def download_code(source: CodeSource) -> Maybe[str]:
    """Download the source code from a given source."""
    if isinstance(source, FromGzip):
        return _parse_string_from_gzip(source)
    elif isinstance(source, FromGist):
        async with httpx.AsyncClient() as client:
            return await download_gist_file(client, source.gist_id, source.filename)


def _parse_string_from_gzip(source: FromGzip) -> Maybe[str]:
    try:
        raw_zipped = base64.urlsafe_b64decode(source.encoded)
    except ValueError:
        return SimpleError("Invalid base64 string")
    decompressed = _gzip_defuse(raw_zipped)
    if isinstance(decompressed, SimpleError):
        return decompressed
    try:
        return decompressed.decode("utf-8")
    except UnicodeDecodeError:
        return SimpleError("Could not decode unicode")


def _gzip_defuse(raw_zipped: bytes) -> Maybe[bytes]:
    """Un-gzip a bytestring while protecting against a zipbomb attack."""
    with gzip.GzipFile(fileobj=io.BytesIO(raw_zipped)) as gzip_file:
        try:
            chunk = gzip_file.read(MAX_GZIP_SIZE_IN_BYTES)
        except zlib.error:
            return SimpleError("Invalid Gzip archive")
        if gzip_file.read(1):
            return SimpleError("Gzip bomb detected")
    return chunk


def parse_code_source(raw_source: object) -> Maybe[CodeSource]:
    """Attempt to turn an unstructured object into a code source."""
    if not isinstance(raw_source, dict):
        return SimpleError("Expected a dict")

    keys = set(raw_source)
    if keys == {"gzip"}:
        if not isinstance(raw_source["gzip"], str):
            return SimpleError("Expected the `gzip` field to be a base64-encoded string")
        return FromGzip(raw_source["gzip"])

    elif keys == {"gist_id", "filename"}:
        return _parse_gist_source(raw_source)

    return SimpleError("Expected either {gzip: ...} or {gist_id: ..., filename: ...}")


def _parse_gist_source(json: dict) -> Maybe[FromGist]:
    if not isinstance(json["gist_id"], str):
        return SimpleError("Expected the `gist_id` field to be a string")
    if not isinstance(json["filename"], str):
        return SimpleError("Expected the `filename` field to be a string")

    return FromGist(gist_id=json["gist_id"], filename=json["filename"])
