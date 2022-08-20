from db_api.deta_db.services import get_all_box, get_all_content_by_box_id, get_box_by_id, search_content_in_box
from misc.keyboards import box_inl_kb

HELP_MESSAGE_TEXT = """Данный бот позволяет сделать маленький и удобный персональный склад.

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

EXAMPLE_BOXES_TEXT = 'Ящик для примера, удалить содержимое, также как и ящик, не получится!\n' \
                     'Можете создать новый /add_box'


async def box_with_contents(box: dict):
    """Представление ящика с его содержимым в текстовом виде"""
    contents = await get_all_content_by_box_id(box_id=box.get('key'))
    contents_list = '\n'.join(content.get('content') for content in contents)
    text = f"<b>{box.get('box_name')}\n{box.get('place')}</b>\n\n" \
           f"Сейчас в ящике:\n{contents_list if contents_list else 'ничего'}"
    return text


async def box_view(user_id: int, box_id: str,
                   menu_only: bool = False,
                   box_menu: bool = False,
                   confirm_menu: bool = False) -> dict:
    """Формирует словарь текст + инлайн клавиатура, а также проверяет
    принадлежность ящика пользователю(который сделал запрос) и существование ящика в системе"""
    box = await get_box_by_id(user_id, box_id)
    if type(box) is dict:
        return {'text': await box_with_contents(box),
                'reply_markup': box_inl_kb(box_id, menu_only, box_menu, confirm_menu)
                }
    elif type(box) is bool:
        return {'text': 'Вы не можете просматривать или редактировать чужие ящики!'}
    return {'text': f'<b>Ящик с таким id {box_id} - не найден.</b>\nПоказать все доступные ящики /all_box'}


def boxes_view(boxes: tuple = None) -> str:
    """Формирует сообщение со списком ящиков данного пользователя"""
    if boxes:
        msg = 'Имя : Место : Ссылка на ящик\n'
        for box in boxes:
            msg += f"\n{box.get('box_name')}: {box.get('place')} /box_{box.get('key')}"
        msg += "\n\nДобавить новый /add_box" \
               f"\nПоиск - отправь мне сообщение(что хочешь найти)"
        return msg
    return 'Нет ящиков.\n\nДобавить новый /add_box'


async def all_boxes_view(user_id: int) -> str:
    """Формирует представление для всех ящиков пользователя в текстовом виде"""
    boxes = await get_all_box(user_id)
    return boxes_view(boxes)


async def search_item_in_box(user_id: int, item: str) -> str:
    """Формирует представление для поиска по всем ящикам"""
    boxes = await search_content_in_box(user_id=user_id, item_to_find=item)
    if boxes:
        return f"<b>Найдено в:</b>\n\n{boxes_view(boxes)}"
    return "Не найдено"
