"""Various interactions with the GitHub API."""

import json
from typing import Dict, TypedDict
from urllib.parse import quote_plus

import httpx

from backend.simple_error import Maybe, SimpleError

API_ROOT = "https://api.github.com"
HTTP_NOT_FOUND = 404


class GistFile(TypedDict):
    filename: str
    language: str
    raw_url: str
    size: int
    content: str  # noqa: WPS110


class Gist(TypedDict):
    files: Dict[str, GistFile]


async def _download_gist(client: httpx.AsyncClient, gist_id: str) -> Maybe[Gist]:
    gist_response = await client.get(
        "https://api.github.com/gists/{0}".format(quote_plus(gist_id)),
        headers={"Accept": "application/vnd.github.v3+json"},
    )
    if gist_response.status_code == HTTP_NOT_FOUND:
        return SimpleError("Gist not found")
    return json.loads(await gist_response.aread())


async def download_gist_file(
    client: httpx.AsyncClient,
    gist_id: str,
    filename: str,
) -> Maybe[str]:
    """
    Download a single file from a single GitHub Gist.

    - Returns `SimpleError` if the gist or the file is not found.
    - Returns `str` with the file contents otherwise.
    """
    gist = await _download_gist(client, gist_id)
    if isinstance(gist, SimpleError):
        return gist

    sought_file = gist["files"].get(filename)
    if sought_file is None:
        return SimpleError("File {0} not present in gist".format(filename))

    return sought_file["content"]
