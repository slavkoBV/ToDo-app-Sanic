import asynctest
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


class TestTodoApp(asynctest.TestCase):
    def test_get_tasks(self):
        response = app.test_client.get('/todo/tasks', gather_request=False)
        self.assertEqual(response.status, 200)
        self.assertTrue('tasks' in response.body.decode())
        self.assertEqual(len(response.json['tasks']), 2)
