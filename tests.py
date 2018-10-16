import json
from asynctest import TestCase
from app import app
from config import TestingConfig
from sqlalchemy import create_engine

from models import Tasks


tasks = [
    {
        'title': 'test1',
        'description': 'test1',
        'status': 'In Progress'
    },
    {
        'title': 'test2',
        'description': 'test2',
        'status': 'Done'
    }
]


class TestTodoApp(TestCase):

    def setUp(self):
        app.config.from_object(TestingConfig)
        app.engine = create_engine("mysql+pymysql://{user}:{password}@{host}/{db}".format(
                                                                                  user=app.config.DB_USER,
                                                                                  db=app.config.DB_NAME,
                                                                                  host=app.config.DB_HOST,
                                                                                  password=app.config.DB_PASSWORD))
        with app.engine.connect() as conn:
            for task in tasks:
                conn.execute(Tasks.insert(),
                             id=None,
                             title=task['title'],
                             description=task['description'],
                             status=task['status']
                             )

    def tearDown(self):
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
        self.assertTrue('tasks' in response.body.decode())

    def test_get_404_for_incorrect_task_id(self):
        response = app.test_client.get('/todo/tasks/3454654434', gather_request=False)
        self.assertEqual(response.status, 404)

    def test_create_task(self):
        data = {
            'title': 'test_create_task',
            'description': 'test_create_description',
            'status': 'Done'
            }
        response = app.test_client.post('/todo/tasks', data=json.dumps(data), gather_request=False)
        self.assertEqual(response.status, 201)
