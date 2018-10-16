from asynctest import TestCase
from app import app


tasks = [
    {
        'id': 1,
        'title': 'test_task',
        'description': 'test',
        'status': 'Done'
    },
    {
        'id': 2,
        'title': 'test2',
        'description': 'test2',
        'status': 'In Progress'
    }
]


class TestTodoApp(TestCase):

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
