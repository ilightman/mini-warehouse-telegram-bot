import logging
import os
from datetime import datetime

from aiogram import Dispatcher, types, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

from handlers.callbacks import register_callbacks
from handlers.message import register_message_handlers

logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s:%(funcName)s:%(message)s', level=logging.INFO)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

ADMIN = os.getenv("ADMIN")


def register_all_handlers(disp: Dispatcher):
    register_callbacks(disp)
    register_message_handlers(disp)


register_all_handlers(dp)


async def admin_notify(disp: Dispatcher, key: str):
    try:
        await disp.bot.send_message(ADMIN,
                                    f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")} '
                                    f'{"Бот запущен и готов к работе" if key == "on" else "Бот выключается"}')
        # print(f'{"Бот запущен и готов к работе" if key == "on" else "Бот выключается"}')
    except Exception as err:
        logging.exception(err)


async def set_default_commands(disp: Dispatcher):
    await disp.bot.set_my_commands([
        types.BotCommand("help", "Помощь"),
        types.BotCommand("add_box", "Добавить ящик"),
        types.BotCommand("all_box", "Отобразить все ящики"),
    ])


async def on_startup(disp: Dispatcher):
    # await admin_notify(disp, key='on')
    await set_default_commands(disp)
    logging.info('Бот запущен и работает')


async def on_shutdown(disp: Dispatcher):
    # await admin_notify(disp, key='off')
    await disp.storage.close()
    await disp.storage.wait_closed()
    logging.info('Бот выключается')
