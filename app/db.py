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


async def start_connection(app) -> None:
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


async def create_tables(db: Pool) -> None:
    """
    Создание таблиц
    :param db: Pool - соединение с базой данных
    """
    async with db.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS links (
            id SERIAL PRIMARY KEY,
            long_url VARCHAR NOT NULL,
            short_url VARCHAR NOT NULL,
            transition_count INT NOT NULL DEFAULT 0);
            ''')
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_short_url 
            ON links(short_url);
            ''')
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_long_url 
            ON links(long_url);
            ''')


async def add_link_to_db(db: Pool, long_url: str, short_url: str) -> None:
    """
    Добавление ссылки в базу данных
    :param db: db: Pool - соединение с базой данных
    :param long_url: str - ссылка на ресурс
    :param short_url: str - короткая ссылка
    """
    async with db.acquire() as conn:
        await conn.execute('''
            INSERT INTO links(long_url, short_url) 
            VALUES ($1, $2)''', long_url, short_url)


async def get_long_url(db: Pool, short_url: str) -> str:
    """
    Получение полной ссылки
    :param db: Pool - соединение с базой данных
    :param short_url: str - короткая ссылка
    :return: str - ссылка на ресурс
    """
    async with db.acquire() as conn:
        result = await conn.fetchval('''
            SELECT long_url FROM links
            WHERE short_url=$1''', short_url)
        return result if result else None


async def get_short_url(db: Pool, long_url: str) -> str:
    """
    Получение короткой ссылки
    :param db: Pool - соединение с базой данных
    :param long_url: str - ссылка на ресурс
    :return: str - короткая ссылка
    """
    async with db.acquire() as conn:
        result = await conn.fetchval('''
            SELECT short_url FROM links
            WHERE long_url=$1''', long_url)
        return result if result else None


async def add_transition(db: Pool, short_url: str) -> None:
    """
    Добавление перехода в счётчик переходов
    :param db: Pool - соединение с базой данных
    :param short_url: str - короткая ссылка
    """
    async with db.acquire() as conn:
        await conn.execute('''
            UPDATE links
            SET transition_count = transition_count + 1
            WHERE short_url=$1''', short_url)


async def get_transition_count(db: Pool, short_url: str) -> int:
    """
    Получение полной ссылки
    :param db: Pool - соединение с базой данных
    :param short_url: str - короткая ссылка
    :return: int - количество переходов по ссылке
    """
    async with db.acquire() as conn:
        result = await conn.fetchval('''
            SELECT transition_count FROM links
            WHERE short_url=$1''', short_url)
        return result


async def check_short_url(db: Pool, short_url: str) -> bool:
    """
    Проверка, существует ли короткая ссылка в базе данных
    :param db: Pool - соединение с базой данных
    :param short_url: str - короткая ссылка
    :return: bool - есть ли такая ссылка в базе данных
    """
    async with db.acquire() as conn:
        result = await conn.fetchval('''
            SELECT 1 FROM links WHERE short_url=$1''', short_url)
        return result is not None
