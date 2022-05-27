import base64
import gzip

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from yarl import URL


def _generate_download_link(base_url: URL, code: str) -> URL:
    return base_url.with_query(gzip=base64.urlsafe_b64encode(gzip.compress(code.encode())).decode())


async def generate_download_link_handler(request: Request) -> Response:
    print(request.base_url)
    print(request.headers)

    try:
        json_data = await request.json()
    except ValueError:
        return Response(status_code=400)

    if (
        not isinstance(json_data, dict)
        or json_data.keys() != {"code", "base_url"}
        or not isinstance(json_data["base_url"], str)
        or not isinstance(json_data["code"], str)
    ):
        return Response(status_code=400)

    try:
        base_url = URL(json_data["base_url"])
    except ValueError:
        return Response(status_code=400)

    code = json_data["code"]
    download_link = _generate_download_link(URL(base_url), code)
    return JSONResponse({
        "download_link": str(download_link),
    })
