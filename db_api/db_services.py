from bot import db


async def get_box_by_id(box_id: str):
    return db.get_box(box_id)


async def get_all_box():
    return db.get_all_box()


async def create_box(box_name):
    return db.create_box(box_name)


async def delete_box(box_id: str):
    db.delete_box(box_id)


async def get_content_by_id(content_id: str):
    return db.select_content(content_id)


async def get_all_content_by_box_id(box_id: str, list_view: bool = False):
    return db.select_all_contents(box_id=box_id, list_view=list_view)


async def add_contents_to_box_by_id(box_id: str, contents_to_add: list):
    db.add_contents_by_box_id(box_id, contents_to_add)


async def delete_content_by_content_id(content_id: str):
    db.delete_contents_by_id(content_id)


async def update_content_name_by_id(content_id: str, value: str):
    return db.update_content_by_content_id(content_id, value)


async def update_box_name_or_place(box_id: str, message_text: str, name: bool = False, place: bool = False):
    db.update_name_or_place(box_id, message_text, name=name, place=place)


async def search_content_in_box(item_to_find: str):
    return db.search_in_box(item_to_find)
