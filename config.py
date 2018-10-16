
class Config:
    DEBUG = False
    TESTING = False
    DB_NAME = 'todo_db'
    DB_USER = 'todo_db_user'
    DB_HOST = '127.0.0.1'
    DB_PASSWORD = 'password'


class TestingConfig(Config):
    TESTING = True
    DB_NAME = 'test_db'
    DB_USER = 'test_db_user'
    DB_HOST = '127.0.0.1'
    DB_PASSWORD = 'password'
