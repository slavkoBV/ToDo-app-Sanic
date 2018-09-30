from sanic import Sanic
from sanic.response import json
import sanic.exceptions

from aiomysql.sa import create_engine
import pymysql
from marshmallow import ValidationError

from forms import TaskForm
from models import Tasks


app = Sanic('todo_app')
app.config.from_pyfile('config.py')


@app.listener('before_server_start')
async def db_init(app, loop):
    app.engine = await create_engine(user=app.config.DB_USER,
                                     db=app.config.DB_NAME,
                                     host=app.config.DB_HOST,
                                     password=app.config.DB_PASSWORD)


@app.listener('after_server_stop')
async def db_close(app, loop):
    app.engine.close()


@app.route('/todo/tasks/', methods=['GET'])
async def get_tasks(request):
    tasks = {}
    async with app.engine.acquire() as conn:
        result = await conn.execute(Tasks.select())
        data = await result.fetchall()
        if data:
            tasks = [dict(task) for task in data]

    return json({'tasks': tasks})


@app.route('/todo/tasks/<task_id:int>', methods=['GET'])
async def get_task_by_id(request, task_id):
    async with app.engine.acquire() as conn:
        result = await conn.execute(Tasks.select().where(Tasks.c.id == task_id))
        data = await result.fetchone()
        task = dict(data) if data else {}  # TODO 404
    return json({'task': task})


@app.route('/todo/tasks/', methods=['POST'])
async def create_task(request):
    errors = None
    status_code = 204
    try:
        form = TaskForm().load(request.json)
        if not form.errors:
            async with app.engine.acquire() as conn:
                try:
                    await conn.execute(Tasks.insert(),
                                       id=None,
                                       title=form.data['title'],
                                       description=form.data['description'],
                                       status=form.data['status'])
                    await conn.connection.commit()
                except pymysql.Error as err:
                    errors = err.args[1]
                    status_code = 400
    except (sanic.exceptions.SanicException, ValidationError) as err:
        status_code = 400
        errors = err.args[1]
    return json({'errors': errors}, status=status_code)


if __name__ == '__main__':
    app.run(host='localhost', port=8000)
