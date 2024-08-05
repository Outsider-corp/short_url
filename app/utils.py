import hashlib
import random
import re
import string

import aiohttp
from asyncpg import Pool

from db import check_short_url


def hash_url(url: str, salt: str = '') -> str:
    """
    Получение 5 последних символов из хеш-значения ссылки (с солью)
    :param url: str - ссылка
    :param salt: str - дополнительные символы
    :return: str - 5 последних символов из хеш-значения ссылки (с солью)
    """
    hashed_url = hashlib.sha256((url + salt).encode())
    return hashed_url.hexdigest()[-5:]


async def create_short_url(db: Pool, long_url: str,
                           max_tries: int = 100) -> str:
    """
    Создание короткой ссылки
    :param db: Pool - подключение в базе данных
    :param long_url: str - ссылка на ресурс
    :param max_tries: int - максимально количество попыток
                            создания короткой ссылки
    :return: str - короткая ссылка из 5 символов
    """
    counter = 0
    salt = ''
    available_chars = string.ascii_letters + string.digits
    while counter < max_tries:
        short_url = hash_url(long_url, salt)
        if not await check_short_url(db, short_url):
            return short_url
        salt = ''.join(random.choices(available_chars, k=5))
        counter += 1


def validate_short_url(short_url: str) -> bool:
    """
    Проверка валидности ссылки
    :param short_url: str - короткая ссылка
    """
    if len(short_url) == 5 and re.match(r'^[a-zA-Z0-9]+$', short_url):
        return True
    return False


async def check_link(link: str, timeout: int = 5) -> bool:
    """
    Проверка доступности ресурса по ссылке link
    :param link: str - url-адрес
    :param timeout: int - время ожидания ответа от ресурса
    :return: bool - доступен ли ресурс
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(link, timeout=timeout) as response:
                return response.status == 200
        except aiohttp.ClientError:
            return False
