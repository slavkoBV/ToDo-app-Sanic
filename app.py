from sanic import Sanic
from sanic import response
from aiomysql.sa import create_engine

from forms import TaskForm, TaskUpdateForm
from models import Tasks

from keep_helper import KeepAPIClient, AuthException

from config import Config
from env_settings import KEEP_USERNAME, KEEP_PASSWORD

app = Sanic('todo_app')
app.config.from_object(Config)


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
    async with app.engine.acquire() as conn:
        result = await conn.execute(Tasks.select())
        data = await result.fetchall()
        tasks = [dict(task) for task in data] if data else {}
    return response.json({'tasks': tasks})


@app.route('/todo/tasks/<task_id:int>', methods=['GET'])
async def get_task_by_id(request, task_id):
    task = None
    errors = None
    status_code = 200
    async with app.engine.acquire() as conn:
        result = await conn.execute(Tasks.select().where(Tasks.c.id == task_id))
        data = await result.fetchone()
        if data:
            task = dict(data)
        else:
            errors = 'Not Found'
            status_code = 404
    return response.json({'task': task, 'errors': errors}, status=status_code)


@app.route('/todo/tasks/', methods=['POST'])
async def create_task(request):
    errors = None
    status_code = 201
    form = TaskForm().load(request.json)
    if not form.errors:
        async with app.engine.acquire() as conn:
            await conn.execute(Tasks.insert(),
                               id=form.data.get('id', None),
                               title=form.data['title'],
                               description=form.data['description'],
                               status=form.data['status'])
            await conn.connection.commit()
    else:
        errors = form.errors
        status_code = 400
    return response.json({'errors': errors}, status=status_code)


@app.route('todo/tasks/<task_id:int>', methods=['DELETE'])
async def delete_task(request, task_id):
    errors = ''
    status_code = 202
    async with app.engine.acquire() as conn:
        query = await conn.execute(Tasks.select().where(Tasks.c.id == task_id))
        task = await query.fetchone()
        if task:
            await conn.execute(Tasks.delete().where(Tasks.c.id == task_id))
            await conn.connection.commit()
        else:
            status_code = 404
            errors = 'Not Found'
    return response.json({'errors': errors}, status_code)


@app.route('/todo/tasks/<task_id:int>', methods=['PUT'])
async def update_task(request, task_id):
    errors = ''
    status_code = 200
    form = TaskUpdateForm().load(request.json)
    if not form.errors:
        async with app.engine.acquire() as conn:
            query = await conn.execute(Tasks.select().where(Tasks.c.id == task_id))
            task = await query.fetchone()
            if task:
                await conn.execute(Tasks.update().where(Tasks.c.id == task_id). \
                                   values({k: v for k, v in form.data.items()}))
                await conn.connection.commit()
            else:
                errors = 'Not Found'
                status_code = 404
    else:
        status_code = 400
        errors = form.errors
    return response.json({'errors': errors}, status=status_code)


@app.route('/todo/tasks/sync', methods=['GET'])
async def sync_tasks_to_keep(request):
    errors = None
    status_code = 200
    async with app.engine.acquire() as conn:
        result = await conn.execute(Tasks.select())
        data = await result.fetchall()
        tasks = [dict(task) for task in data]
        nodes = [(task['title'], True if task['status'] == 'Done' else False) for task in tasks]
        try:
            keep = KeepAPIClient(KEEP_USERNAME, KEEP_PASSWORD)
            await keep.sync_todo_list(nodes)
        except AuthException as err:
            errors = err.args
            status_code = 401
    return response.json({'errors': errors}, status_code)


if __name__ == '__main__':
    app.run(host='localhost', port=8000)
