import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from db_api.db_services import search_content_in_box, update_box_name_or_place, update_content_name_by_id, \
    add_contents_to_box_by_id, create_box
from misc import boxes_list, inl_kb_generator, box_from_db, cancel_inl_kb


async def start_command(message: types.Message):
    # "Выбрать ящик /box_<b>номер ящика</b>\n" \
    msg = "Показать все ящики /all_box\n" \
          "Добавить новый ящик /add_box\n" \
          "Для поиска отправьте любое слово\n"
    await message.answer(msg)


async def help_command(message: types.Message):
    msg = """Данный бот позволяет сделать маленький и удобный персональный склад.

Структура - ящик, в котором есть содержимое. 

Ящики можно добавлять, удалять, 
а также менять их название и место где они находятся. 

Содержимое аналогично с ящиками - можно добавлять, 
удалять, а также редактировать название (например количество чего-то было 2 а стало 1)

Команды и подсказки бота помогут с этим разобраться.
Команды всего три:
- /all_box - отобразит все ящики
- /add_box - добавить новый ящик
- введи любое название и бот будет искать его в ящиках"""
    await message.answer(msg)


async def all_box(message: types.Message):
    """Отображение всех ящиков с названием и расположением"""
    await message.answer(await boxes_list())
    logging.info(f'{message.from_user.id}:{message.from_user.full_name}')


async def select_box_by_number(message: types.Message):
    """Отображение ящика по команде /box_номерящика или номерящика"""
    box_id = message.text[5:] if message.text.startswith('/box_') else message.text
    msg = await box_from_db(box_id)
    if msg:
        await message.answer(msg, reply_markup=inl_kb_generator(box_id, menu_only=True))
        logging.info(f'/box_{box_id}:{message.from_user.id}:{message.from_user.full_name}')
    else:
        await message.answer(f'<b>Ящик с таким id {box_id} - не найден.</b>\n'
                             'Показать все доступные ящики /all_box')
        logging.error(f'{box_id} not found:{message.from_user.id}:{message.from_user.full_name}')


async def add_box(message: types.Message, state: FSMContext):
    await message.answer("Введи имя нового ящика:", reply_markup=cancel_inl_kb)
    await state.set_state('add_name')
    logging.info(f'{message.from_user.id}:{message.from_user.full_name}')


async def add_name_handler(message: types.Message, state: FSMContext):
    box_name = message.text.title()
    if box_name.startswith('/'):
        await message.delete()
        await state.set_state('add_name')
        logging.error(f'failed:"/"in_name:{message.from_user.id}:{message.from_user.full_name}')
    elif box_name:
        box_id = await create_box(box_name)
        if box_id:
            await message.answer(await box_from_db(box_id), reply_markup=inl_kb_generator(box_id, menu_only=True))
            await state.finish()
            logging.info(f'success:{box_id}:{message.from_user.id}:{message.from_user.full_name}')
        else:
            await message.answer("Уже есть ящик с таким именем, давай еще раз")
            await state.set_state('add_name')


async def add_contents(message: types.Message, state: FSMContext):
    contents_to_add = [value.strip().lower() for value in message.text.split(',')]
    data = await state.get_data()
    box_id = data.get('box_id')
    await add_contents_to_box_by_id(box_id, contents_to_add)
    await message.answer(await box_from_db(box_id), reply_markup=inl_kb_generator(box_id, menu_only=True))
    await state.finish()
    logging.info(f'{message.from_user.id}:{message.from_user.full_name}')


async def edit_content_item(message: types.Message, state: FSMContext):
    content = await state.get_data('content_id')
    content_id = content.get('content_id')
    if message.text.startswith('/'):
        await message.delete()
        await state.set_state('edit_item')
        logging.error(f'failed:{message.from_user.id}:{message.from_user.full_name}')
    else:
        value = message.text.lower()
        box_id = await update_content_name_by_id(content_id, value)
        await message.answer(await box_from_db(box_id), reply_markup=inl_kb_generator(box_id, menu_only=True))
        await state.finish()
        logging.info(f'success:{message.from_user.id}:{message.from_user.full_name}')


async def update_name_place(message: types.Message, state: FSMContext):
    n_state = await state.get_state()
    message_text = message.text
    await message.delete()
    if message_text.startswith('/'):
        await state.set_state('upd_name' if n_state == 'upd_name' else 'upd_place')
        logging.error(f'failed:{message.from_user.id}:{message.from_user.full_name}')
    else:
        box_id = await state.get_data('box_id')
        box_id = box_id.get('box_id')
        if n_state == "upd_name":
            await update_box_name_or_place(box_id, message_text, name=True)
        if n_state == "upd_place":
            await update_box_name_or_place(box_id, message_text, place=True)
        await message.answer(f"Новое имя: {message_text}\n\n" + await box_from_db(box_id),
                             reply_markup=inl_kb_generator(box_id, menu_only=True))
        await state.finish()
        logging.info(f'success:{message.from_user.id}:{message.from_user.full_name}')


async def search(message: types.Message):
    """Поиск по содержимому ящиков при любом состоянии"""
    response = await search_content_in_box(message.text.lower())
    if response:
        await message.answer(f"<b>Найдено в:</b>\n\n{await boxes_list(response)}")
    else:
        await message.answer("Не найдено")
    logging.info(f'{message.from_user.id}:{message.from_user.full_name}:{message.text}')


def register_message_handlers(disp: Dispatcher):
    disp.register_message_handler(start_command, commands='start')
    disp.register_message_handler(help_command, commands='help')

    disp.register_message_handler(all_box, commands='all_box')
    disp.register_message_handler(add_box, commands="add_box")
    disp.register_message_handler(select_box_by_number, regexp=r'^/box_([a-zA-Z0-9]{1,})$')
    disp.register_message_handler(add_name_handler, state="add_name")
    disp.register_message_handler(add_contents, state="add_contents")
    disp.register_message_handler(edit_content_item, state="edit_item")
    disp.register_message_handler(update_name_place, state="upd_name")
    disp.register_message_handler(update_name_place, state="upd_place")
    disp.register_message_handler(search)
