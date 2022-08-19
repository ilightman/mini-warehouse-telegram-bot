from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from db_api.db_services import get_box_by_id, get_all_content_by_box_id, get_all_box

cb_kb = CallbackData('kb', 'box_id', 'action')

cancel_inl_kb = InlineKeyboardMarkup(row_width=1)
cancel_inl_kb.add(InlineKeyboardButton(text='отмена', callback_data=cb_kb.new(box_id='cancel', action='cancel')))


def inl_kb_generator(box_id: str,
                     menu_only: bool = False,
                     box_menu: bool = False,
                     confirm_menu: bool = False) -> InlineKeyboardMarkup:
    menu_dict = {'Изменить содержимое': 'edit_items', 'Добавить в ящик': 'edit_contents',
                 'Изменить имя': 'edit_name', 'Изменить место': 'edit_place',
                 'Удалить содержимое': 'delete_contents_by_id',
                 'Удалить ящик': 'delete_confirm'}  # , 'Назад': 'back'
    inl_kb = InlineKeyboardMarkup(row_width=1)
    if menu_only:
        inl_kb.add(InlineKeyboardButton(text='Меню', callback_data=cb_kb.new(box_id=box_id, action='menu')))
    elif box_menu:
        for key, value in menu_dict.items():
            inl_kb.add(InlineKeyboardButton(text=key, callback_data=cb_kb.new(box_id=box_id, action=value)))
    elif confirm_menu:
        inl_kb = InlineKeyboardMarkup(row_width=2)
        inl_kb.add(InlineKeyboardButton(text='Да', callback_data=cb_kb.new(box_id=box_id, action='confirm')),
                   InlineKeyboardButton(text='Назад', callback_data=cb_kb.new(box_id=box_id, action='back')))
    return inl_kb


async def box_from_db(box_id):
    box = await get_box_by_id(box_id)
    if box:
        contents = await get_all_content_by_box_id(box_id=box_id, list_view=True)
        msg = f"<b>{box.get('box_name')}\n{box.get('place')}</b>\n\n" \
              "Сейчас в ящике:\n" \
              f"{contents if contents else 'ничего'}"
        return msg
    else:
        return ''


async def edit_contents_inl(box_id: str, cb_data_prefix: str) -> InlineKeyboardMarkup:
    """Генерирует inline клавиатуру с кнопками-содержимое ящика"""
    contents = await get_all_content_by_box_id(box_id)
    contents_kb = InlineKeyboardMarkup(row_width=1)
    for item in contents:
        contents_kb.add(InlineKeyboardButton(text=item.get('contents'),
                                             callback_data=cb_kb.new(
                                                 box_id=box_id,
                                                 action=f"{cb_data_prefix}{item.get('key')}")))
    contents_kb.add(InlineKeyboardButton(text='Назад', callback_data=cb_kb.new(box_id=box_id, action='back')))
    return contents_kb


async def boxes_list(tuple_of_boxes: tuple = ()) -> str:
    box_list = tuple_of_boxes if tuple_of_boxes else await get_all_box()
    if box_list:
        boxes = '\n'.join(
            f"{box.get('box_name')}: {box.get('place')} /box_{box.get('key')}" for box in box_list)
        return f"Имя : Место : Ссылка на ящик\n\n{boxes}\n\nДобавить новый /add_box" \
               f"\nПоиск - отправь мне сообщение(что хочешь найти)"
    return 'Нет ящиков.\n\nДобавить новый /add_box'
