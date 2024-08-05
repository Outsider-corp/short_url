from aiohttp import web
from app.routers import get_routers
from app.db import close_connection, start_connection, create_tables


async def main():
    app = web.Application()

    app.on_startup.append(start_connection)
    app.on_startup.append(lambda x: create_tables(x['db']))

    app.add_routes(get_routers())

    app.on_cleanup.append(close_connection)

    return app


if __name__ == '__main__':
    web.run_app(main())
