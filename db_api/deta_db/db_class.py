from typing import List, Union

from deta import Deta


class DetaDB:
    """Класс для работы с Deta Base"""

    def __init__(self, project_key: Union[str, None] = None, project_id: Union[str, None] = None):
        self._db = Deta(project_key=project_key, project_id=project_id)
        self.users = self._db.Base('users')
        self.boxes = self._db.Base('boxes')
        self.contents = self._db.Base('contents')

    def get_user(self, user_id: str) -> dict:
        """Получает пользователя из БД"""
        user = self.users.get(key=user_id)
        return user

    def create_user(self, user_id: str, username: str, first_name: str, is_admin: bool = False) -> dict:
        """Создает пользователя в БД и тестовый ящик"""
        user = self.users.put(data={
            'username': username,
            'first_name': first_name,
            'is_admin': is_admin,
        }, key=user_id)
        # Добавление тестового ящика
        self.boxes.put(data={
            'user_id': user_id,
            'box_name': 'Пример ящика',
            'place': 'верхняя полка',
        }, key=user_id)
        # Добавление тестового содержимого
        self.contents.put_many(items=[
            {
                'content': 'чехол iPhone 6s plus',
                'box_key': user_id,
            },
            {
                'content': 'наушники',
                'box_key': user_id,
            },
            {
                'content': 'джойстик',
                'box_key': user_id,
            }
        ])
        return user

    def get_box(self, box_id) -> Union[dict, None]:
        """Возвращает ящик box_id """
        box = self.boxes.get(key=box_id)
        return box

    def get_all_box(self, user_id: str) -> Union[List[dict], None]:
        """Показать все ящики пользователя"""
        res = self.boxes.fetch({'user_id': user_id})
        return res.items

    def create_box(self, user_id: str, box_name: str) -> str:
        """Создает новый ящик с именем box_name и возвращает его id в базе данных"""
        box = self.boxes.insert(
            {
                'user_id': user_id,
                'box_name': box_name,
                'place': 'Не указано',
            }
        )
        box_id = box.get('key')
        return box_id

    def update_name_or_place(self, box_id, value, name: bool = False, place: bool = False):
        """Изменяет имя или место ящика"""
        updates = {}
        if name:
            updates['box_name'] = value
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

    def add_contents_to_box(self, user_id: str, box_id: str, values: list) -> None:
        """Добавить в ящик содержимое из списка values"""
        for value in values:
            if len(value) <= 2:
                continue
            self.contents.put({
                'content': value,
                'box_key': box_id,
                'user_id': user_id,
            })

    def select_content(self, content_id: str) -> Union[dict, None]:
        """Возвращает содержимое c content_id"""
        contents = self.contents.get(key=content_id)
        return contents

    def select_all_contents(self, box_id: str) -> Union[List[dict], None]:
        """Возвращает содержимое ящика с номером - box_id"""
        result = self.contents.fetch({'box_key': box_id})
        return result.items

    def update_content_by_content_id(self, content_id: str, value: str) -> str:
        """Обновляет значение содержимого content_id на value, возвращает новое значение """
        self.contents.update({'content': value}, key=content_id)
        content = self.contents.get(key=content_id)
        return content.get('box_key')

    def delete_contents_by_id(self, content_id) -> None:
        """Удаляет содержиое по его content_id"""
        self.contents.delete(key=content_id)

    def search_in_box(self, user_id: str, item: str):
        """Ищет во всех ящиках указаное слово item"""
        if len(item) < 3:
            return None
        result = self.contents.fetch({'content?contains': item, 'user_id': user_id})
        if not result:
            return None
        box_ids = set()
        for content in result.items:
            box_key = content.get('box_key')
            box_ids.add(box_key)
        return tuple(self.get_box(box_key) for box_key in box_ids)
