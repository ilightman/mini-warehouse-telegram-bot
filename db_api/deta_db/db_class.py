from typing import List, Union

from deta import Deta


class DetaDB:
    """Класс для работы с Deta Base"""

    def __init__(self, project_key: Union[str, None] = None,
                 project_id: Union[str, None] = None,
                 users_base_name: str = 'users',
                 boxes_base_name: str = 'boxes',
                 contents_base_name: str = 'contents'
                 ):
        self._db = Deta(project_key=project_key, project_id=project_id)
        self.users = self._db.Base(users_base_name)
        self.boxes = self._db.Base(boxes_base_name)
        self.contents = self._db.Base(contents_base_name)

    def create_user(self, user_id: str, username: str, first_name: str, is_admin: bool = False) -> dict:
        """Создает пользователя в БД и тестовый ящик"""
        user = self.users.put(data={
            'username': username,
            'first_name': first_name,
            'is_admin': is_admin,
        }, key=user_id)

        return user

    def get_user(self, user_id: str) -> dict:
        """Получает пользователя из БД"""
        user = self.users.get(key=user_id)
        return user

    def create_box(self, user_id: str, name: str) -> dict:
        """Создает новый ящик с именем name и возвращает его id в базе данных"""
        box = self.boxes.insert(
            {
                'user_id': user_id,
                'name': name,
                'place': 'Не указано',
            }
        )
        return box

    def get_box(self, box_id) -> Union[dict, None]:
        """Возвращает ящик box_id """
        box = self.boxes.get(key=box_id)
        return box

    def get_all_box(self, user_id: str) -> Union[List[dict], None]:
        """Возвращает все ящики пользователя"""
        res = self.boxes.fetch({'user_id': user_id})
        return res.items

    def update_box_name_or_place(self, box_id, value, name: bool = False, place: bool = False):
        """Изменяет имя или место ящика"""
        updates = {}
        if name:
            updates['name'] = value
        if place:
            updates['place'] = value.lower()
        self.boxes.update(updates=updates, key=box_id)
        return self.boxes.get(key=box_id)

    def delete_box(self, box_id) -> None:
        """Удаляет ящик с id - box_id"""
        self.boxes.delete(key=box_id)
        result = self.contents.fetch({'box_key': box_id})
        for contents in result.items:
            self.contents.delete(key=contents.get('key'))

    def add_content_to_box(self, user_id: str, box_id: str, values: list) -> None:
        """Добавить в ящик содержимое из списка values"""
        for value in values:
            if len(value) <= 2:
                continue
            self.contents.put({
                'name': value,
                'box_key': box_id,
                'user_id': user_id,
            })

    def get_content(self, content_id: str) -> Union[dict, None]:
        """Возвращает содержимое c content_id"""
        content = self.contents.get(key=content_id)
        return content

    def get_all_contents(self, box_id: str) -> Union[List[dict], None]:
        """Возвращает содержимое ящика с номером - box_id"""
        result = self.contents.fetch({'box_key': box_id})
        return result.items

    def update_content_name(self, content_id: str, name: str) -> dict:
        """Обновляет значение содержимого content_id на name, возвращает новое значение """
        self.contents.update({'name': name}, key=content_id)
        content = self.contents.get(key=content_id)
        return content

    def delete_content(self, content_id: str) -> None:
        """Удаляет содержиое по его content_id"""
        self.contents.delete(key=content_id)

    def search_in_all_box_contents(self, user_id: str, item: str) -> Union[None, set[str]]:
        """Ищет во всех ящиках указанное слово item"""
        if len(item) < 3:
            return None
        result = self.contents.fetch({'name?contains': item, 'user_id': user_id})
        if not result:
            return None
        box_ids = set()
        for content in result.items:
            box_key = content.get('box_key')
            box_ids.add(box_key)
        return box_ids
