from asynctest import TestCase
from app import app
from config import TestingConfig
from aiomysql.sa import create_engine


class TestTodoApp(TestCase):

    def setUp(self):
        app.config.from_object(TestingConfig)
        app.engine = create_engine(user=app.config.DB_USER,
                                   db=app.config.DB_NAME,
                                   host=app.config.DB_HOST,
                                   password=app.config.DB_PASSWORD)

    def tearDown(self):
        app.engine.close()

    def test_get_tasks(self):
        response = app.test_client.get('/todo/tasks', gather_request=False)
        self.assertEqual(response.status, 200)
        self.assertTrue('tasks' in response.body.decode())

    def test_get_task_by_id(self):
        response = app.test_client.get('/todo/tasks/1', gather_request=False)
        self.assertEqual(response.status, 200)

    def test_get_404_task_by_incorrect_id(self):
        response = app.test_client.get('/todo/tasks/3454654434asasasa', gather_request=False)
        self.assertEqual(response.status, 404)
