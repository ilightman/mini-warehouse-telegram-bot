import os

import pytest
from dotenv import load_dotenv
from db_api.deta_db.db_class import DetaDB


@pytest.fixture(scope='module')
def db():
    load_dotenv()
    project_key = os.getenv('PROJECT_KEY')
    project_id = os.getenv('PROJECT_ID')

    db = DetaDB(project_key=project_key, project_id=project_id,
                users_base_name='test_users',
                boxes_base_name='test_boxes',
                contents_base_name='text_contents')
    db.boxes.put_many(items=[
        {
            'key': '1',
            'user_id': '1',
            'name': 'TestBox1',
            'place': 'upper_test',
        }, {
            'key': '11',
            'user_id': '1',
            'name': 'TestBox2',
            'place': 'lower_test',
        }])
    db.contents.put_many(items=[
        {
            'key': '1',
            'name': 'test_content_1',
            'box_key': '1',
            'user_id': '1',
        },
        {
            'key': '2',
            'name': 'test_content_2',
            'box_key': '1',
            'user_id': '1',
        },
        {
            'key': '3',
            'name': 'test_content_1',
            'box_key': '11',
            'user_id': '1',
        }
    ])
    yield db
    for user in db.users.fetch().items:
        db.users.delete(user['key'])
    for box in db.boxes.fetch().items:
        db.boxes.delete(box['key'])
    for content in db.contents.fetch().items:
        db.contents.delete(content['key'])


class TestDbClass:
    @pytest.fixture
    def test_user(self):
        return {
            'user_id': '2',
            'first_name': 'Testname',
            'is_admin': False,
            'username': 'testusername',
        }

    @pytest.fixture
    def test_db_user(self):
        return {
            'key': '2',
            'first_name': 'Testname',
            'is_admin': False,
            'username': 'testusername',
        }

    def test_create_user(self, db, test_user, test_db_user):
        user_from_db = db.create_user(**test_user)
        assert user_from_db == test_db_user

    def test_get_user(self, db, test_user, test_db_user):
        user_from_db = db.get_user(test_user['user_id'])
        assert user_from_db == test_db_user

    def test_create_box(self, db, test_user):
        test_box = {
            'name': 'Пример ящика',
            'user_id': '2',
            'place': 'Не указано'
        }
        box = db.create_box(user_id=test_user['user_id'],
                            name=test_box['name'])
        assert box['name'] == test_box['name']
        assert box['place'] == test_box['place']
        assert box['user_id'] == test_box['user_id']

    def test_get_box(self, db):
        test_db_box = {
            'key': '1',
            'user_id': '1',
            'name': 'TestBox1',
            'place': 'upper_test',
        }
        box = db.get_box("1")
        assert box == test_db_box

    def test_get_all_box(self, db):
        boxes = db.get_all_box('1')
        boxes_in_db = [{
            'key': '1',
            'user_id': '1',
            'name': 'TestBox1',
            'place': 'upper_test',
        }, {
            'key': '11',
            'user_id': '1',
            'name': 'TestBox2',
            'place': 'lower_test',
        }]
        assert boxes == boxes_in_db

    def test_update_name_or_place(self, db):
        box = db.boxes.get('11')
        test_box = {
            'key': '11',
            'user_id': '1',
            'name': 'TestBox2',
            'place': 'lower_test',
        }
        assert box == test_box
        test_box['name'] = 'UpdatedTestBox2'
        box = db.update_box_name_or_place(box_id='11', value='UpdatedTestBox2', name=True)
        assert box == test_box
        test_box['place'] = 'updated_place'
        box = db.update_box_name_or_place(box_id='11', value='Updated_Place', place=True)
        assert box == test_box

    def test_delete_box(self, db):
        box = db.boxes.fetch({'user_id': '2'}).items[0]
        box_key = box.get('key')
        db.delete_box(box_key)
        assert db.get_box(box_key) is None

    def test_add_content_to_box(self, db):
        result = db.contents.fetch({'box_key': '11', 'user_id': '1'}).items
        names_in_box_content = tuple(content.get('name') for content in result)
        assert 'test_value1' not in names_in_box_content
        assert 'test_value2' not in names_in_box_content

        db.add_content_to_box(user_id='1', box_id='11', values=['test_value1', 'test_value2'])
        result = db.contents.fetch({'box_key': '11', 'user_id': '1'}).items
        names_in_box_content = tuple(content.get('name') for content in result)
        assert 'test_value1' in names_in_box_content
        assert 'test_value2' in names_in_box_content

    def test_get_content(self, db):
        test_content = {
            'key': '2',
            'name': 'test_content_2',
            'box_key': '1',
            'user_id': '1',
        }
        content = db.get_content('2')
        assert content == test_content

    def test_get_all_contents(self, db):
        test_contents = [
            {
                'key': '1',
                'name': 'test_content_1',
                'box_key': '1',
                'user_id': '1',
            },
            {
                'key': '2',
                'name': 'test_content_2',
                'box_key': '1',
                'user_id': '1',
            }
        ]
        contents = db.get_all_contents('1')
        assert contents == test_contents

    def test_update_content_name(self, db):
        old_content = db.contents.get('1')
        test_content = {
            'key': '1',
            'name': 'test_content_1',
            'box_key': '1',
            'user_id': '1',
        }
        assert old_content == test_content
        test_content['name'] = 'updated_test_content_1'
        content = db.update_content_name('1', 'updated_test_content_1')
        assert content == test_content

    def test_delete_content(self, db):
        content = db.contents.get('2')
        assert content is not None
        db.delete_content('2')
        assert db.contents.get('2') is None

    def test_search_in_all_box_contents(self, db):
        result = db.search_in_all_box_contents(user_id='1', item='test_content_1')
        assert result == {'1', '11'}


@pytest.mark.asyncio
class TestDbServices:
    pass
    # async def test_create_user(self, db):
    #     user_mock = AsyncMock(id=1, username='testusername', first_name='test_first_name')
    #     await create_user(user_mock, is_admin=False)
    #     print(user_mock.__dict__)
