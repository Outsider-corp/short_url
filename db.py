from asyncpg import create_pool, Pool
from config import POSTGRES_HOST, POSTGRES_PASS, POSTGRES_PORT, POSTGRES_USER, \
    POSTGRES_DB


async def connection() -> Pool:
    """
    Создание соединения с базой данных
    :return: Pool - пул соединений
    """
    connection_url = (f'postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@'
                      f'{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')

    pool = await create_pool(connection_url)

    return pool


async def start_connection(app):
    """
    Открытие соединения с базой данных
    :param app: web.Application - объект приложения
    """
    app['db'] = await connection()


async def close_connection(app):
    """
    Закрытие соединения с базой данных
    :param app: web.Application - объект приложения
    """
    await app['db'].close()


async def create_tables(db):
    """
    Создание таблиц
    :param db: web.Application - объект приложения
    """
    async with db.acquire() as conn:
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS links (
        id SERIAL PRIMARY KEY,
        long_url VARCHAR NOT NULL,
        short_url VARCHAR NOT NULL)
        ''')

        await conn.execute('''
                CREATE TABLE IF NOT EXISTS transitions (
                id SERIAL PRIMARY KEY,
                transition_count int NOT NULL,
                FOREIGN KEY (id) REFERENCES
                links(id))
                ''')

async def add_link_to_db(db, long_url: str, short_url: str):
    """
    Добавление ссылки в базу данных
    :param db:
    :param long_url:
    :param short_url:
    :return:
    """