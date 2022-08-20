from typing import Iterable

from aiogram.types import User

from db_api.db_config import db


async def create_user(user: User, is_admin: bool = False):
    db.create_user(str(user.id), user.username, user.first_name, is_admin=is_admin)


async def check_user(user: User):
    user_from_db = db.get_user(user_id=str(user.id))
    if not user_from_db:
        await create_user(user)


async def get_box_by_id(user_id: int, box_id: str):
    box = db.get_box(box_id)
    if box.get('user_id') == str(user_id):
        return db.get_box(box_id)
    return False


async def get_all_box(user_id: int):
    return db.get_all_box(str(user_id))


async def create_box(user_id: int, box_name: str):
    return db.create_box(str(user_id), box_name)


async def delete_box(box_id: str):
    db.delete_box(box_id)


async def get_content_by_id(content_id: str):
    return db.select_content(content_id)


async def get_all_content_by_box_id(box_id: str, list_view: bool = False):
    contents = db.select_all_contents(box_id=box_id)
    if list_view:
        return '\n'.join(content.get('content') for content in contents)
    return contents


async def add_contents_to_box_by_id(user_id: int, box_id: str, contents_to_add: Iterable[str]):
    db.add_contents_by_box_id(str(user_id), box_id, contents_to_add)


async def delete_content_by_content_id(content_id: str):
    db.delete_contents_by_id(content_id)


async def update_content_name_by_id(content_id: str, value: str):
    return db.update_content_by_content_id(content_id, value)


async def update_box_name_or_place(box_id: str, message_text: str, name: bool = False, place: bool = False):
    db.update_name_or_place(box_id, message_text, name=name, place=place)


async def search_content_in_box(user_id: int, item_to_find: str):
    result = db.search_in_box(str(user_id), item_to_find)
    if result:
        return result
    return None
