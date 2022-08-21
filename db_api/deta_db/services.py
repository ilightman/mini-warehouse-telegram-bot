from typing import Iterable, Union, Tuple

from aiogram.types import User
from pydantic import BaseModel

from db_api.db_config import db


class Box(BaseModel):
    key: str
    name: str
    place: str
    user_id: str


class Content(BaseModel):
    key: str
    name: str
    box_key: str
    user_id: str


async def create_user(user: User, is_admin: bool = False) -> None:
    """Создает пользователя в БД. Вызывает метод класса БД"""
    db.create_user(str(user.id), user.username, user.first_name, is_admin=is_admin)


async def check_user(user: User) -> None:
    """Проверяет есть ли пользователь в БД, если нет то создает его. Вызывает метод класса БД"""
    user_from_db = db.get_user(user_id=str(user.id))
    if not user_from_db:
        await create_user(user)


async def get_box(user_id: int, box_id: str) -> Union[Box, bool, None]:
    """Получает ящик для указанного пользователя и проверяет его ли это ящик. Вызывает метод класса БД"""
    box = db.get_box(box_id)
    if box:
        box = Box.parse_obj(box)
        if box.user_id == str(user_id):
            return box
        return False
    return None


async def get_all_box(user_id: int) -> Union[Tuple[Box, ...], None]:
    """Получает все ящики для указанного пользователя. Вызывает метод класса БД"""
    boxes = db.get_all_box(str(user_id))
    if boxes:
        box_tuple = tuple(Box.parse_obj(box) for box in boxes)
        return box_tuple
    return None


async def create_box(user_id: int, box_name: str) -> Box:
    """Создает ящик для указанного пользователя и возвращает id ящика. Вызывает метод класса БД"""
    box = db.create_box(str(user_id), box_name)
    return Box.parse_obj(box)


async def delete_box(box_id: str) -> None:
    """Удаляет ящик с указанным id. Вызывает метод класса БД"""
    db.delete_box(box_id)


async def get_content_by_id(content_id: str) -> Union[Content, None]:
    """Получает содержимое по его id. Вызывает метод класса БД"""
    content = db.get_content(content_id)
    return Content.parse_obj(content)


async def get_all_content_by_box_id(box_id: str) -> Union[Tuple[Content, ...], None]:
    """Получает всё содержимое ящика по id-ящика. Вызывает метод класса БД"""
    contents = db.get_all_contents(box_id=box_id)
    if contents:
        contents_tuple = tuple(Content.parse_obj(content) for content in contents)
        return contents_tuple
    return None


async def add_contents_to_box_by_id(user_id: int, box_id: str, contents_to_add: Iterable[str]) -> None:
    """Добавляет содержимое из списка в ящик. Вызывает метод класса БД"""
    db.add_content_to_box(str(user_id), box_id, contents_to_add)


async def delete_content_by_content_id(content_id: str) -> None:
    """Удаляет содержимое в ящике по его content_id. Вызывает метод класса БД"""
    db.delete_content(content_id)


async def update_content_name_by_id(content_id: str, value: str) -> Content:
    """Обновляет имя содержимого в ящике и возвращает box_id. Вызывает метод класса БД"""
    content = db.update_content_name(content_id, value)
    return Content.parse_obj(content)


async def update_box_name_or_place(box_id: str, message_text: str, name: bool = False, place: bool = False) -> None:
    """Обновляет имя или место ящика. Вызывает метод класса БД"""
    db.update_box_name_or_place(box_id, message_text, name=name, place=place)


async def search_content_in_box(user_id: int, item_to_find: str) -> Union[Tuple[Box, ...], None]:
    """Ищет item_to_find в ящиках пользователя. Вызывает метод класса БД"""
    box_ids = db.search_in_all_box_contents(str(user_id), item_to_find)
    if box_ids:
        boxes_tuple = tuple(Box.parse_obj(db.get_box(box_id)) for box_id in box_ids)
        return boxes_tuple
    return None
