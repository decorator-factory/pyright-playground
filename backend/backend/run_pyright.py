"""Run Pyright on a Python file."""


import asyncio
import contextlib
import json
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Optional

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

MAX_REQUEST_BODY_BYTES = 10**7


async def run_pyright(req: Request) -> Response:
    """HTTP handler for the /pyright endpoint."""
    body = await _read_at_most(req, MAX_REQUEST_BODY_BYTES)

    if body is None:
        return Response()

    try:
        json_body = json.loads(body)
    except ValueError:
        return JSONResponse({"status": "fail", "error": "Expected JSON"})

    if not isinstance(json_body, dict):
        return JSONResponse({"status": "fail", "error": "Expected an object"})

    code = json_body.get("code")

    if not isinstance(code, str):
        return JSONResponse({"status": "fail", "error": "Expected a 'code' field with a string"})

    pyright_output = await _run_pyright_on_code("1.1.301", code)

    return JSONResponse(pyright_output)


async def _read_at_most(req: Request, limit: int) -> Optional[bytes]:
    chunks: list[bytes] = []
    length_so_far = 0
    async for chunk in req.stream():
        length_so_far += len(chunk)
        if length_so_far > limit:
            return None

        chunks.append(chunk)
    return b"".join(chunks)


@contextlib.asynccontextmanager
async def _async_tempfile(file_content: str, suffix: str) -> AsyncGenerator[Path, None]:
    file = await asyncio.to_thread(  # noqa: WPS110
        lambda: tempfile.NamedTemporaryFile("r+", suffix=suffix),
    )
    await asyncio.to_thread(lambda: file.write(file_content) and file.flush())
    try:
        yield Path(file.name)
    finally:
        await asyncio.to_thread(file.close)


async def _run_pyright_on_code(version: str, code: str) -> object:
    async with _async_tempfile(code, ".py") as file_path:
        command = ["node", "lang-server/index.js", "--outputjson", str(file_path)]

        process = await asyncio.subprocess.create_subprocess_exec(
            *command,
            env={"PYRIGHT_VERSION": version},
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _stderr = await process.communicate()
    return json.loads(stdout)
