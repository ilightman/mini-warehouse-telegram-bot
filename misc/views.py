import logging

from db_api.deta_db.services import get_all_box, get_all_content_by_box_id, get_box, search_content_in_box, Box
from locales.i18n_config import i18n
from misc.keyboards import box_inl_kb

_ = i18n.gettext

HELP_MESSAGE_TEXT = _("""Данный бот позволяет сделать маленький и удобный персональный склад.

Структура - ящик, в котором есть содержимое. 

Ящики можно добавлять, удалять, 
а также менять их название и место где они находятся. 

Содержимое аналогично с ящиками - можно добавлять, 
удалять, а также редактировать название (например количество чего-то было 2 а стало 1)

Команды и подсказки бота помогут с этим разобраться.
Команды всего три:
- /all_box - отобразит все ящики
- /add_box - добавить новый ящик
- введи любое название и бот будет искать его в ящиках""")

EXAMPLE_BOXES_TEXT = _(
    'Ящик для примера, удалить содержимое, также как и ящик, не получится!{}Можете создать новый /add_box').format('\n')

MSG_LIST_FOOTER = "\n\n📦" + _("/add_box - добавить новый ящик") + \
                  "\n🔎 " + _("поиск - просто отправь что хочешь найти")


async def box_with_contents(box: Box):
    """Представление ящика с его содержимым в текстовом виде"""
    text = f"📦<b>{box.name}\n📍{box.place}</b>" + \
           "\n\n📋" + _("Сейчас в ящике:")
    contents = await get_all_content_by_box_id(box_id=box.key)
    if contents:
        contents_list = '\n- '.join(content.name for content in contents)
        text += f"\n- {contents_list}"
    else:
        text += '\n - ' + _('ничего')
    return text


async def box_view(user_id: int, box_id: str,
                   menu_only: bool = False,
                   box_menu: bool = False,
                   confirm_menu: bool = False) -> dict:
    """Формирует словарь текст + инлайн клавиатура, а также проверяет
    принадлежность ящика пользователю(который сделал запрос) и существование ящика в системе"""
    box = await get_box(user_id, box_id)
    if type(box) is Box:
        return {'text': await box_with_contents(box),
                'reply_markup': box_inl_kb(box_id, menu_only, box_menu, confirm_menu)
                }
    elif type(box) is bool:
        logging.warning(f'{user_id} is forbidden to open {box_id}')
    return {'text': _('❌ Ящик <b>{box_id} - не найден</b>.').format(box_id=box_id) + MSG_LIST_FOOTER}


def boxes_view(boxes: tuple[Box] = None) -> str:
    """Формирует сообщение со списком ящиков данного пользователя"""
    if boxes:
        msg = _('📛Имя|📍Место|🔗️Ссылка на ящик') + '\n'
        for index, box in enumerate(boxes, 1):
            msg += f"\n{index}. {box.name} | {box.place} <b>/box_{box.key}</b>"
        msg += MSG_LIST_FOOTER
        return msg
    return '❌ ' + _('<b>У Вас пока нет ящиков.</b>') + MSG_LIST_FOOTER


async def all_boxes_view(user_id: int) -> str:
    """Формирует представление для всех ящиков пользователя в текстовом виде"""
    boxes = await get_all_box(user_id)
    return boxes_view(boxes)


async def search_item_in_box(user_id: int, item: str) -> str:
    """Формирует представление для поиска по всем ящикам"""
    boxes = await search_content_in_box(user_id=user_id, item_to_find=item)
    if boxes:
        return "🔎 <b>" + _("Найдено в:") + f"</b>\n\n{boxes_view(boxes)}"
    return "❌ " + _("<b>Не найдено</b>, попробуйте ввести часть слова")
