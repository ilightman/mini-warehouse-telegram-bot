from typing import List, Union

from deta import Deta


class DB:

    def __init__(self, project_key: Union[str, None] = None, project_id: Union[str, None] = None):
        self._db = Deta(project_key=project_key, project_id=project_id)
        self.users = self._db.Base('users')
        self.boxes = self._db.Base('boxes')
        self.contents = self._db.Base('contents')

    def get_all_box(self) -> Union[List[dict], None]:
        """Показать все ящики"""
        res = self.boxes.fetch()
        return res.items

    def create_box(self, box_name) -> Union[str, None]:
        """Создает новый ящик с именем box_name и возвращает его id в базе данных или None в случае ошибки"""
        box = self.boxes.insert(
            {
                'box_name': box_name,
                'place': 'Не указано',
            }
        )
        return box.get('key')
        # Except :
        #   return None

    def delete_box(self, box_id) -> None:
        """Удаляет ящик с id - box_id"""
        self.boxes.delete(key=box_id)
        result = self.contents.fetch({'box_key': box_id})
        for contents in result.items:
            self.contents.delete(key=contents.get('key'))

    def get_box(self, box_id) -> Union[dict, None]:
        """Возвращает ящик box_id """
        box = self.boxes.get(key=box_id)
        return box

    def select_content(self, content_id: str) -> Union[dict, None]:
        """Возвращает содержимое c content_id"""
        contents = self.contents.get(key=content_id)
        return contents

    def update_content_by_content_id(self, content_id: str, value: str) -> str:
        """Обновляет значение содержимого content_id на value, возвращает новое значение """
        self.contents.update({'contents': value}, key=content_id)
        content = self.contents.get(key=content_id)
        return content.get('box_key')

    def select_all_contents(self, box_id: str, list_view: bool = False):
        result = self.contents.fetch({'box_key': box_id})
        if list_view:
            return '\n'.join(content.get('contents') for content in result.items)
        else:
            return result.items

    def add_contents_by_box_id(self, box_id: str, values: list) -> None:
        """Добавить в ящик содержимое из списка values"""
        for value in values:
            if len(value) >= 2:
                self.contents.put({
                    'contents': value,
                    'box_key': box_id,
                })
            else:
                continue

    def delete_contents_by_id(self, content_id):
        self.contents.delete(key=content_id)

    def update_name_or_place(self, box_id, value, name: bool = False, place: bool = False):
        updates = {}
        if name:
            updates['box_name'] = value
        if place:
            updates['place'] = value
        self.boxes.update(updates=updates, key=box_id)
        return self.boxes.get(key=box_id)

    def search_in_box(self, item):
        if len(item) < 3:
            return []
        result = self.contents.fetch({'contents?contains': item})
        if result:
            result_tuple = tuple(self.get_box(content.get('box_key')) for content in result.items)

            return result_tuple
        return None
