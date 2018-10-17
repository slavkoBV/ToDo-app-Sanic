import json
from asynctest import TestCase, patch, CoroutineMock
from app import app
from config import TestingConfig
from sqlalchemy import create_engine

from models import Tasks

app.config.from_object(TestingConfig)

# test data
tasks = [
    {
        'id': 1,
        'title': 'test1',
        'description': 'test1',
        'status': 'In Progress'
    },
    {
        'id': 2,
        'title': 'test2',
        'description': 'test2',
        'status': 'Done'
    }
]


class TestTodoApp(TestCase):

    def setUp(self):
        """Connect to test_db, which must be created manually. Table tasks also must be created manually.
         Primary Key (id) must not be auto increment."""

        app.engine = create_engine("mysql+pymysql://{user}:{password}@{host}/{db}".format(
                                                                                       user=app.config.DB_USER,
                                                                                       db=app.config.DB_NAME,
                                                                                       host=app.config.DB_HOST,
                                                                                       password=app.config.DB_PASSWORD))
        with app.engine.connect() as conn:
            # Fill test_db with test data
            for task in tasks:
                conn.execute(Tasks.insert(),
                             id=task['id'],
                             title=task['title'],
                             description=task['description'],
                             status=task['status']
                             )

    def tearDown(self):
        """Clear test_db (Delete all row in tasks table)"""
        app.engine = create_engine("mysql+pymysql://{user}:{password}@{host}/{db}".format(
                                                                                    user=app.config.DB_USER,
                                                                                    db=app.config.DB_NAME,
                                                                                    host=app.config.DB_HOST,
                                                                                    password=app.config.DB_PASSWORD))
        with app.engine.connect() as conn:
            conn.execute(Tasks.delete())

    def test_get_tasks(self):
        response = app.test_client.get('/todo/tasks', gather_request=False)
        self.assertEqual(response.status, 200)
        self.assertEqual(len(response.json['tasks']), 2)

    def test_get_task_by_id(self):
        response = app.test_client.get('/todo/tasks/1', gather_request=False)
        self.assertEqual(response.status, 200)

    def test_get_404_for_incorrect_task_id(self):
        response = app.test_client.get('/todo/tasks/3454654434', gather_request=False)
        self.assertEqual(response.status, 404)

    def test_create_task(self):
        data = {
            'id': 3,
            'title': 'test_create_task',
            'description': 'test_create_description',
            'status': 'Done'
            }
        response = app.test_client.post('/todo/tasks', data=json.dumps(data), gather_request=False)
        self.assertEqual(response.status, 201)

    def test_update_task(self):
        data = {
            'id': 2,
            'title': 'change_title'
        }
        response = app.test_client.put('/todo/tasks/{}'.format(data['id']), data=json.dumps(data), gather_request=False)
        app.engine = create_engine("mysql+pymysql://{user}:{password}@{host}/{db}".format(
                                                                                    user=app.config.DB_USER,
                                                                                    db=app.config.DB_NAME,
                                                                                    host=app.config.DB_HOST,
                                                                                    password=app.config.DB_PASSWORD))
        with app.engine.connect() as conn:
            res = conn.execute(Tasks.select().where(Tasks.c.id == data['id']))
            result = res.fetchone()
        self.assertEqual(response.status, 200)
        self.assertEqual(result['id'], data['id'])

    def test_update_task_with_incorrect_id(self):
        data = {
            'id': 5,
            'title': 'test'
        }
        response = app.test_client.put('/todo/tasks/{}'.format(data['id']), data=json.dumps(data), gather_request=False)
        self.assertEqual(response.status, 404)

    @patch("keep_helper.KeepAPIClient.sync_todo_list", new_callable=CoroutineMock)
    @patch("keep_helper.KeepAPIClient.__init__")
    def test_sync_to_keep(self, mock_init, mock_sync ):
        mock_init.return_value = None
        response = app.test_client.get('/todo/tasks/sync', gather_request=False)
        self.assertEqual(response.status, 200)
        nodes = [(task['title'], True if task['status'] == 'Done' else False) for task in tasks]
        mock_sync.assert_awaited_once_with(nodes)
