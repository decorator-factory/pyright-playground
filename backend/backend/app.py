"""
Entry point to the application
"""


import os

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

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

_static_path = os.getenv("STATIC_PATH", os.path.join(__file__, "..", "frontend", "public"))
_index_path = os.path.join(_static_path, "index.html")

app = Starlette(
    routes=[
        Route("/pyright", run_pyright, methods=["POST"]),
        Route("/download_code", download_code_handler, methods=["GET", "POST"]),
        Route("/download_link", generate_download_link_handler, methods=["POST"]),
        Route("/", FileResponse(_index_path)),
        Mount("/", StaticFiles(directory=_static_path)),
    ],
    middleware=[_cors_middleware],
)
