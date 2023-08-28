import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, CommandHelp
# from aiogram.utils.deep_linking import get_start_link

from db_api.deta_db.services import update_box_name_or_place, update_content_name_by_id, \
    add_contents_to_box_by_id, create_box, check_user
# from locales.i18n_config import i18n
from misc.keyboards import cancel_inl_kb
from misc.views import box_view, HELP_MESSAGE_TEXT, search_item_in_box, all_boxes_view

# _ = i18n.gettext


async def start_command(message: types.Message):
    await check_user(user=message.from_user)
    # args = message.get_args()
    # if args:
    #     await message.answer(args)
    #     return
    # msg = await get_start_link(payload='box_309329130')
    # await message.answer(msg)
    await message.answer(message.as_json())
    # msg = (
    #     "Показать все ящики /all_box{sr}Добавить новый ящик /add_box{sr}Для поиска отправьте любое слово{sr}").format(
    #     sr='\n')
    # await message.answer(msg)


async def help_command(message: types.Message):
    """Отвечает текстом на команду /help"""
    msg = HELP_MESSAGE_TEXT
    await message.answer(msg)


async def all_box(message: types.Message):
    """Отображение всех ящиков с названием и расположением"""
    msg = await all_boxes_view(user_id=message.from_user.id)
    await message.answer(msg)
    logging.info(f'{message.from_user.id}')


async def select_box_by_number(message: types.Message):
    """Отображение ящика по команде /box_номерящика или номерящика"""
    box_id = message.text[5:] if message.text.startswith('/box_') else message.text
    msg_dict = await box_view(user_id=message.from_user.id, box_id=box_id, menu_only=True)
    await message.answer(**msg_dict)
    logging.info(f'/box_{box_id}:{message.from_user.id}')


async def add_box(message: types.Message, state: FSMContext):
    """Создает новый ящик для текущего пользователя"""
    await message.answer(("Введи имя нового ящика:"), reply_markup=cancel_inl_kb)
    await state.set_state('add_name')
    logging.info(f'{message.from_user.id}')


async def add_name_handler(message: types.Message, state: FSMContext):
    """Добавляет имя новому ящику для текущего пользователя"""
    box_name = message.text.title()
    if box_name.startswith('/'):
        await message.delete()
        await state.set_state('add_name')
        logging.error(f'failed:"/"in_name:{message.from_user.id}')
    elif box_name:
        box = await create_box(user_id=message.from_user.id, box_name=box_name)
        box_id = box.key
        msg_dict = await box_view(user_id=message.from_user.id, box_id=box_id, menu_only=True)
        await message.answer(**msg_dict)
        await state.finish()
        logging.info(f'success:{box_id}:{message.from_user.id}')


async def add_contents(message: types.Message, state: FSMContext):
    """Добавляет содержимое в ящик пользователя"""
    contents_to_add = tuple(value.strip().lower() for value in message.text.split(',') if not value.startswith('/'))
    data = await state.get_data()
    box_id = data.get('box_id')
    await add_contents_to_box_by_id(message.from_user.id, box_id, contents_to_add)
    msg_dict = await box_view(user_id=message.from_user.id, box_id=box_id, menu_only=True)
    await message.answer(**msg_dict)
    await state.finish()
    logging.info(f'{message.from_user.id}')


async def edit_content_item(message: types.Message, state: FSMContext):
    """Изменяет имя содержимого в ящике"""
    content = await state.get_data('content_id')
    content_id = content.get('content_id')
    await message.delete()
    if message.text.startswith('/'):
        await state.set_state('edit_item')
        logging.error(f'failed:{message.from_user.id}')
    else:
        value = message.text.lower()
        content = await update_content_name_by_id(content_id, value)
        msg_dict = await box_view(user_id=message.from_user.id, box_id=content.box_key, menu_only=True)
        await message.answer(**msg_dict)
        await state.finish()
        logging.info(f'success:{message.from_user.id}')


async def update_name_place(message: types.Message, state: FSMContext):
    """Изменяет имя или место ящика"""
    n_state = await state.get_state()
    message_text = message.text
    await message.delete()
    if message_text.startswith('/'):
        await state.set_state('upd_name' if n_state == 'upd_name' else 'upd_place')
        logging.error(f'failed:{message.from_user.id}')
    else:
        box_id = await state.get_data('box_id')
        box_id = box_id.get('box_id')
        if n_state == "upd_name":
            await update_box_name_or_place(box_id, message_text, name=True)
        if n_state == "upd_place":
            await update_box_name_or_place(box_id, message_text, place=True)
        msg_dict = await box_view(user_id=message.from_user.id, box_id=box_id, menu_only=True)
        await message.answer(("Информация обновлена:") + "\n\n" + msg_dict['text'],
                             reply_markup=msg_dict['reply_markup'])
        await state.finish()
        logging.info(f'success:{message.from_user.id}')


async def search(message: types.Message):
    """Поиск по содержимому ящиков"""
    msg = await search_item_in_box(
        user_id=message.from_user.id,
        item=message.text.lower())
    await message.answer(msg)
    logging.info(f'{message.from_user.id}:{message.text}')


def register_message_handlers(dp: Dispatcher):
    """Регистрирует все message_handlers в текущем файле"""
    dp.register_message_handler(start_command, CommandStart())
    dp.register_message_handler(help_command, CommandHelp())

    dp.register_message_handler(all_box, commands='all_box')
    dp.register_message_handler(add_box, commands="add_box")
    dp.register_message_handler(select_box_by_number, regexp=r'^/box_([a-zA-Z0-9]{1,})$')
    dp.register_message_handler(add_name_handler, state="add_name")
    dp.register_message_handler(add_contents, state="add_contents")
    dp.register_message_handler(edit_content_item, state="edit_item")
    dp.register_message_handler(update_name_place, state="upd_name")
    dp.register_message_handler(update_name_place, state="upd_place")
    dp.register_message_handler(search)
