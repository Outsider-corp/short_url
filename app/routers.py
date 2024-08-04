from aiohttp import web
from aiohttp import ClientError

from app.utils import create_short_url, validate_short_url
from db import add_link_to_db, get_long_url, add_transition, \
    get_transition_count


async def generate_short_url(request: web.Request):
    """
    Создание короткой ссылки
    :param request: web.Request - объект запроса
    """
    data = await request.post()
    long_url = data.get('long_url')
    if not long_url:
        return ClientError()
    database = request.app['db']
    short_url = await create_short_url(database, long_url)
    if short_url:
        try:
            await add_link_to_db(database, long_url, short_url)
            return web.json_response({'short_url': short_url})
        except Exception as e:
            return web.json_response({'status_code': 400, 'reason': e})
    return web.json_response({'status_code': 500,
                              'reason': "Can't create short url."})


async def transit_url(request: web.Request):
    """
    Переход по короткой ссылке
    :param request: web.Request - объект запроса
    """
    short_url = request.match_info.get('short_url')
    if not validate_short_url(short_url):
        return web.json_response(
            {'status_code': 400, 'reason': 'Invalid link.'})
    database = request.app['db']
    long_url = await get_long_url(database, short_url)
    print(long_url)
    if long_url:
        await add_transition(database, short_url)
        raise web.HTTPFound(long_url)
    return web.json_response({'status_code': 404,
                              'reason': f'No link for {short_url}'})


async def transition_count(request: web.Request):
    """
    Выдача количества переходов по ссылке
    :param request: web.Request - объект запроса
    """
    short_url = request.match_info.get('short_url')

    database = request.app['db']
    transition_count = await get_transition_count(database, short_url)
    if transition_count is not None:
        return web.json_response({'status_code': 200,
                                  'transition_count': transition_count})
    return web.json_response({'status_code': 404,
                              'reason': f'No link for {short_url}'})


def get_routers():
    """Получение списка роутеров."""
    return [web.post('/api/generate_short_url', generate_short_url),
            web.post('/{short_url}', transit_url),
            web.get('/api/count/{short_url}', transition_count)]
