from app.main import app
from starlette.staticfiles import StaticFiles
from starlette.middleware.wsgi import WSGIMiddleware
from starlette.applications import Starlette

starlette_app = Starlette()
starlette_app.mount("/static", StaticFiles(directory="static"), name="static")
starlette_app.mount("/", WSGIMiddleware(app))

asgi_app = starlette_app