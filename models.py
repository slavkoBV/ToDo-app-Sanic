from sqlalchemy import Table, Column, Integer, String, Enum, MetaData


metadata = MetaData()

Tasks = Table(
    'tasks',
    metadata,
    Column('id', Integer, unique=True, primary_key=True, autoincrement=True),
    Column('title', String(30)),
    Column('description', String(100)),
    Column('status', Enum('To Do', 'In Progress', 'Review', 'Done')))
