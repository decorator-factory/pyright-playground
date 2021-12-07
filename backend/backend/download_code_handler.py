from starlette.requests import Request
from starlette.responses import Response

from backend.download_code import download_code, parse_code_source
from backend.simple_error import SimpleError

HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404


async def download_code_handler(request: Request) -> Response:
    """
    HTTP handler for the /download_code endpoint.

    This endpoint accepts query params, in either of these variants:
    - gzip: string

    - gist_id: string
      filename: string
    """
    raw_source = dict(request.query_params)
    source = parse_code_source(raw_source)
    if isinstance(source, SimpleError):
        error = "Invalid request: {0}".format(source.message)
        return Response(error, status_code=HTTP_BAD_REQUEST)

    code = await download_code(source)
    if isinstance(code, SimpleError):
        error = "Could not fetch code: {0}".format(code.message)
        return Response(error, status_code=HTTP_NOT_FOUND)

    return Response(code)
