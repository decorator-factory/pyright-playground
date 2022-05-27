"""
Simple service for running Pyright on a piece of code.

Export an ASGI application with a single `/pyright` endpoint.
The endpoint accepts a JSON body like {"code": string} and returns
the JSON that pyright produced on this file.
"""

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route

from backend.better_middleware import BetterMiddleware
from backend.download_code_handler import download_code_handler
from backend.generate_download_link import generate_download_link_handler
from backend.run_pyright import run_pyright

_cors_middleware = BetterMiddleware(lambda app: CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["content-type"],
))

app = Starlette(
    routes=[
        Route("/pyright", run_pyright, methods=["POST"]),
        Route("/download_code", download_code_handler, methods=["GET", "POST"]),
        Route("/download_link", generate_download_link_handler, methods=["POST"]),
    ],
    middleware=[_cors_middleware],
)
