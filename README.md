# ToDo app

ToDo list RESTful application

## Built with
* [Sanic](https://sanic.readthedocs.io/en/latest/) - The Flask-like Python 3.5+ web server
* [aiomysql](https://aiomysql.readthedocs.io/en/latest/) -  The library for accessing a MySQL database from the asyncio 
* [marshmallow](https://marshmallow.readthedocs.io/en/3.0/) - The ORM/ODM/framework-agnostic library for converting complex datatypes, such as objects, to and from native Python datatypes

## Endpoints
- GET /todo/tasks/                                   - get all tasks from todolist
- POST /todo/tasks/ 
    --data {"title", "description", "status"}        - create new task in todolist
- GET /todo/tasks/<task_id:int>                      - get task with ID == task_id
- PUT /todo/tasks/<task_id:int> 
    --data {"title" or "description" or "status"}    - update task with ID == task_id
- DELETE /todo/tasks/<task_id:int>                   - delete task with ID == task_id
- GET /todo/tasks/sync                               - synchronize todolist with Google Keep ToDo)list  