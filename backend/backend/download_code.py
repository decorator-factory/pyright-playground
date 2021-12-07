import base64
import gzip
import io
import re
import zlib
from dataclasses import dataclass
from typing import Union

import httpx

from backend.github import download_gist_file, download_github_issue
from backend.simple_error import Maybe, SimpleError


@dataclass(frozen=True)
class FromGzip:
    encoded: str


@dataclass(frozen=True)
class FromGist:
    gist_id: str
    filename: str


@dataclass(frozen=True)
class FromGithubIssue:
    owner: str
    repo: str
    issue_number: int


CodeSource = Union[FromGzip, FromGist, FromGithubIssue]


HTTP_NOT_FOUND = 404
MAX_GZIP_SIZE_IN_BYTES = 65536


async def download_code(source: CodeSource) -> Maybe[str]:
    """Download the source code from a given source."""
    if isinstance(source, FromGzip):
        return _parse_string_from_gzip(source)
    elif isinstance(source, FromGist):
        async with httpx.AsyncClient() as client:
            return await download_gist_file(client, source.gist_id, source.filename)
    elif isinstance(source, FromGithubIssue):
        async with httpx.AsyncClient() as client:  # noqa: WPS440
            issue = await download_github_issue(
                client,
                source.owner,
                source.repo,
                source.issue_number,
            )
        if isinstance(issue, SimpleError):
            return issue
        return _extract_code_from_markdown(issue["body"])


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


def _extract_code_from_markdown(code: str) -> Maybe[str]:
    match = re.search(r"```py((?:.|\n)+?)```", code)
    if match is None:
        return SimpleError("Code object not found in the issue")
    return match[1]


def parse_code_source(raw_source: object) -> Maybe[CodeSource]:
    """Attempt to turn an unstructured object into a code source."""
    if not isinstance(raw_source, dict):
        return SimpleError("Expected a dict")

    keys = set(raw_source)
    if keys == {"gzip"}:
        return _parse_gzip_source(raw_source)

    elif keys == {"gist_id", "filename"}:
        return _parse_gist_source(raw_source)

    elif keys == {"issue"}:
        return _parse_github_issue_source(raw_source)

    return SimpleError("Expected either (gzip) or (gist_id,filename) or (owner,repo,issue)")


def _parse_gzip_source(raw_source: dict) -> Maybe[FromGzip]:
    if not isinstance(raw_source["gzip"], str):
        return SimpleError("Expected the `gzip` field to be a base64-encoded string")
    return FromGzip(raw_source["gzip"])


def _parse_github_issue_source(raw_source: dict) -> Maybe[FromGithubIssue]:
    if not isinstance(raw_source["issue"], str):
        return SimpleError("Expected the `issue` field to be a string")

    match = re.match(r"([a-zA-Z_-]+)/([a-zA-Z_-]+)/(\d+)", raw_source["issue"])
    if match is None:
        return SimpleError("Expected the `issue` field to be `owner/repo/issue_number`")

    owner, repo, issue_number = match.groups()
    return FromGithubIssue(owner=owner, repo=repo, issue_number=int(issue_number))


def _parse_gist_source(raw_source: dict) -> Maybe[FromGist]:
    if not isinstance(raw_source["gist_id"], str):
        return SimpleError("Expected the `gist_id` field to be a string")
    if not isinstance(raw_source["filename"], str):
        return SimpleError("Expected the `filename` field to be a string")

    return FromGist(gist_id=raw_source["gist_id"], filename=raw_source["filename"])
