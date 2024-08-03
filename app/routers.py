from aiohttp import web
from aiohttp import ClientError

from app.utils import create_short_url


async def generate_short_url(request: web.Request):
    """
    Создание короткой ссылки
    :param request:
    :return:
    """
    data = await request.post()
    long_url = data.get('long_url')

    if not long_url:
        return ClientError()
    short_url = create_short_url(long_url)

    add_link_to_db()
    return web.Response(body={'short_url': short_url})


async def transit_url(request):
    """
    Переход по короткой ссылке
    :param request:
    :return:
    """
    return web.Response(body={'status_code': 200})


async def transition_count(request):
    """
    Выдача количества переходов по ссылке
    :param request:
    :return:
    """
    return web.Response()


def get_routers():
    """Получение списка роутеров."""
    return [web.post('/api/generate_short_url', generate_short_url),
            web.post('/', transit_url),
            web.get('/api/count', transition_count)]
