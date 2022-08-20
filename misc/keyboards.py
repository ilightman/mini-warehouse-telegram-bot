from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from db_api.deta_db.services import get_all_content_by_box_id

cb_kb = CallbackData('kb', 'action', 'box_id')  # , 'content_id')

cancel_inl_kb = InlineKeyboardMarkup(row_width=1)
cancel_inl_kb.add(InlineKeyboardButton(text='отмена', callback_data=cb_kb.new(box_id='', action='cancel')))


def box_inl_kb(box_id: str,
               menu_only: bool = False,
               box_menu: bool = False,
               confirm_menu: bool = False) -> InlineKeyboardMarkup:
    """Формирует инлайн-клавиатуру с указанными параметрами"""
    menu_dict = {'Изменить содержимое': 'edit_items', 'Добавить в ящик': 'edit_contents',
                 'Изменить имя': 'edit_name', 'Изменить место': 'edit_place',
                 'Удалить содержимое': 'delete_content',
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


async def box_content_inl_kb(box_id: str, action: str) -> InlineKeyboardMarkup:
    """Генерирует inline клавиатуру с кнопками-содержимое ящика (для редактирования или удаления)"""
    contents = await get_all_content_by_box_id(box_id)
    contents_kb = InlineKeyboardMarkup(row_width=1)
    for content in contents:
        contents_kb.add(InlineKeyboardButton(text=content.name,
                                             callback_data=cb_kb.new(
                                                 box_id=box_id,
                                                 action=f"{action}{content.key}")))
    contents_kb.add(InlineKeyboardButton(text='Назад', callback_data=cb_kb.new(box_id=box_id, action='back')))
    return contents_kb
