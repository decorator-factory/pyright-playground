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


async def _download_gist(client: httpx.AsyncClient, gist_id: str) -> Maybe[Gist]:
    gist_response = await client.get(
        "{0}/gists/{1}".format(API_ROOT, quote_plus(gist_id)),
        headers={"Accept": "application/vnd.github.v3+json"},
    )
    if gist_response.status_code == HTTP_NOT_FOUND:
        return SimpleError("Gist not found")
    return json.loads(await gist_response.aread())


class GithubIssueRaw(TypedDict):
    #: Markdown body of the issue
    body: str
    title: str


async def download_github_issue(
    client: httpx.AsyncClient,
    owner: str,
    repo: str,
    issue_number: int,
) -> Maybe[GithubIssueRaw]:
    """
    Download a single file from its identifier.

    - Returns `SimpleError` if the issue was not found
    - Returns a `GithubIssueRaw` otherwise
    """
    owner = quote_plus(owner)
    repo = quote_plus(repo)
    url = "{0}/repos/{owner}/{repo}/issues/{issue_number}".format(
        API_ROOT,
        owner=owner,
        repo=repo,
        issue_number=issue_number,
    )
    response = await client.get(
        url,
        headers={"Accept": "application/vnd.github.v3.raw+json"},
    )
    if response.status_code == HTTP_NOT_FOUND:
        return SimpleError("Issue {0}/{1} not found".format(repo, issue_number))

    return json.loads(await response.aread())
