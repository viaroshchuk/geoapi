from aiohttp.web import (
    Application,
    run_app,
)

from app.api.v1 import routes
from app.db import init_db


def init() -> Application:
    app = Application()
    app.add_routes(routes)
    app['db_engine'] = init_db()
    return app


if __name__ == '__main__':
    application = init()
    run_app(application)
