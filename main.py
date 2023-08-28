import os

from aiogram import types, Dispatcher, Bot
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from bot import bot, dp, on_startup, on_shutdown

app = FastAPI(docs_url=None, redoc_url=None)
BOT_TOKEN = os.getenv('BOT_TOKEN')
SECRET_TOKEN = os.getenv('SECRET_TOKEN')
DETA_URL = os.getenv('DETA_URL')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
WEBHOOK_URL = DETA_URL + WEBHOOK_PATH
API_TELEGRAM_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'


@app.on_event('startup')
async def startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )
    await on_startup(dp)


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict, request: Request):
    telegram_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
    if telegram_token == SECRET_TOKEN:
        tlg_update = types.Update(**update)
        Dispatcher.set_current(dp)
        Bot.set_current(bot)
        await dp.process_update(tlg_update)
        return JSONResponse(content={'success': True}, status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(content={'detail': 'Not authorized, secret token header is not provided!'},
                            status_code=status.HTTP_401_UNAUTHORIZED)


@app.get('/docs')
@app.get('/redocs')
@app.get('/')
@app.get(WEBHOOK_PATH)
async def get_webhook():
    return JSONResponse(content={'detail': 'Not authorized! You are not supposed to be here!'},
                        status_code=status.HTTP_403_FORBIDDEN)


@app.on_event('shutdown')
async def shutdown():
    await on_shutdown(dp)
    await bot.session.close()


@app.get('/init')
async def test():
    return {
        'webhook_url': WEBHOOK_URL,
        'get_webhook_method': API_TELEGRAM_URL + '/getwebhookinfo',
        'set_webhook_link': API_TELEGRAM_URL + f'/setWebhook?'
                                               f'url={WEBHOOK_URL}'
                                               f'&secret_token={SECRET_TOKEN}'
                                               f'&drop_pending_updates=True',
        'delete_webhook_link': API_TELEGRAM_URL + '/deleteWebhook',
    }
