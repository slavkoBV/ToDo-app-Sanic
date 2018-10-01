from sanic import Sanic
from sanic.response import json
import sanic.exceptions

from aiomysql.sa import create_engine
import pymysql
from marshmallow import ValidationError

from forms import TaskForm, TaskUpdateForm
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
        tasks = [dict(task) for task in data] if data else {}
    return json({'tasks': tasks})


@app.route('/todo/tasks/<task_id:int>', methods=['GET'])
async def get_task_by_id(request, task_id):
    task = None
    async with app.engine.acquire() as conn:
        result = await conn.execute(Tasks.select().where(Tasks.c.id == task_id))
        data = await result.fetchone()
        if data:
            task = dict(data)
        else:
            raise sanic.exceptions.abort(404)
    return json({'task': task})


@app.route('/todo/tasks/', methods=['POST'])
async def create_task(request):
    errors = None
    status_code = 204
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
    else:
        errors = form.errors
        status_code = 400
    return json({'errors': errors}, status=status_code)


@app.route('todo/tasks/<task_id:int>', methods=['DELETE'])
async def delete_task(request, task_id):
    errors = ''
    task = None
    status_code = 202
    async with app.engine.acquire() as conn:
        try:
            query = await conn.execute(Tasks.select().where(Tasks.c.id == task_id))
            task = await query.fetchone()
            await conn.execute(Tasks.delete().where(Tasks.c.id == task_id))
            await conn.connection.commit()
        except pymysql.Error as err:
            errors = err.args[1]
            status_code = 400
    if not task:
        status_code = 404
        errors = 'Not Found'
    return json({'errors': errors}, status_code)


@app.route('/todo/tasks/<task_id:int>', methods=['PUT'])
async def update_task(request, task_id):
    errors = ''
    status_code = 200
    task = None
    form = TaskUpdateForm().load(request.json)
    if not form.errors:
        async with app.engine.acquire() as conn:
            try:
                query = await conn.execute(Tasks.select().where(Tasks.c.id == task_id))
                task = await query.fetchone()
                await conn.execute(Tasks.update().where(Tasks.c.id == task_id).\
                                   values({k: v for k, v in form.data.items()}))
                await conn.connection.commit()
            except pymysql.Error as err:
                errors = err.args[1]
                status_code = 400
    if not task:
        errors = 'Not Found'
        status_code=404
    return json({'errors': errors}, status=status_code)


if __name__ == '__main__':
    app.run(host='localhost', port=8000)
