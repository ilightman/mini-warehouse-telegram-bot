import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, CommandHelp
from aiogram.utils.deep_linking import get_start_link

from db_api.deta_db.services import update_box_name_or_place, update_content_name_by_id, \
    add_contents_to_box_by_id, create_box, check_user
from misc.keyboards import cancel_inl_kb
from misc.views import box_view, HELP_MESSAGE_TEXT, search_item_in_box, all_boxes_view


async def start_command(message: types.Message):
    await check_user(user=message.from_user)
    # args = message.get_args()
    # if args:
    #     await message.answer(args)
    #     return
    # msg = await get_start_link(payload='box_309329130')
    # await message.answer(msg)

    msg = "Показать все ящики /all_box\n" \
          "Добавить новый ящик /add_box\n" \
          "Для поиска отправьте любое слово\n"
    await message.answer(msg)


async def help_command(message: types.Message):
    msg = HELP_MESSAGE_TEXT
    await message.answer(msg)


async def all_box(message: types.Message):
    """Отображение всех ящиков с названием и расположением"""
    await message.answer(await all_boxes_view(user_id=message.from_user.id))
    logging.info(f'{message.from_user.id}')


async def select_box_by_number(message: types.Message):
    """Отображение ящика по команде /box_номерящика или номерящика"""
    box_id = message.text[5:] if message.text.startswith('/box_') else message.text
    msg_dict = await box_view(user_id=message.from_user.id, box_id=box_id, menu_only=True)
    await message.answer(**msg_dict)
    logging.info(f'/box_{box_id}:{message.from_user.id}')


async def add_box(message: types.Message, state: FSMContext):
    await message.answer("Введи имя нового ящика:", reply_markup=cancel_inl_kb)
    await state.set_state('add_name')
    logging.info(f'{message.from_user.id}')


async def add_name_handler(message: types.Message, state: FSMContext):
    box_name = message.text.title()
    if box_name.startswith('/'):
        await message.delete()
        await state.set_state('add_name')
        logging.error(f'failed:"/"in_name:{message.from_user.id}')
    elif box_name:
        box_id = await create_box(user_id=message.from_user.id, box_name=box_name)
        msg_dict = await box_view(user_id=message.from_user.id, box_id=box_id, menu_only=True)
        await message.answer(**msg_dict)
        await state.finish()
        logging.info(f'success:{box_id}:{message.from_user.id}')


async def add_contents(message: types.Message, state: FSMContext):
    contents_to_add = tuple(value.strip().lower() for value in message.text.split(','))
    data = await state.get_data()
    box_id = data.get('box_id')
    await add_contents_to_box_by_id(message.from_user.id, box_id, contents_to_add)
    msg_dict = await box_view(user_id=message.from_user.id, box_id=box_id, menu_only=True)
    await message.answer(**msg_dict)
    await state.finish()
    logging.info(f'{message.from_user.id}')


async def edit_content_item(message: types.Message, state: FSMContext):
    content = await state.get_data('content_id')
    content_id = content.get('content_id')
    await message.delete()
    if message.text.startswith('/'):
        await state.set_state('edit_item')
        logging.error(f'failed:{message.from_user.id}')
    else:
        value = message.text.lower()
        box_id = await update_content_name_by_id(content_id, value)
        msg_dict = await box_view(user_id=message.from_user.id, box_id=box_id, menu_only=True)
        await message.answer(**msg_dict)
        await state.finish()
        logging.info(f'success:{message.from_user.id}')


async def update_name_place(message: types.Message, state: FSMContext):
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
        await message.answer(f"Информация обновлена:\n\n" + msg_dict['text'], reply_markup=msg_dict['reply_markup'])
        await state.finish()
        logging.info(f'success:{message.from_user.id}')


async def search(message: types.Message):
    """Поиск по содержимому ящиков"""
    msg = await search_item_in_box(
        user_id=message.from_user.id,
        item=message.text.lower())
    await message.answer(msg)
    logging.info(f'{message.from_user.id}:{message.text}')


def register_message_handlers(disp: Dispatcher):
    disp.register_message_handler(start_command, CommandStart())
    disp.register_message_handler(help_command, CommandHelp())

    disp.register_message_handler(all_box, commands='all_box')
    disp.register_message_handler(add_box, commands="add_box")
    disp.register_message_handler(select_box_by_number, regexp=r'^/box_([a-zA-Z0-9]{1,})$')
    disp.register_message_handler(add_name_handler, state="add_name")
    disp.register_message_handler(add_contents, state="add_contents")
    disp.register_message_handler(edit_content_item, state="edit_item")
    disp.register_message_handler(update_name_place, state="upd_name")
    disp.register_message_handler(update_name_place, state="upd_place")
    disp.register_message_handler(search)
