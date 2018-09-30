from marshmallow import Schema, fields
from marshmallow.validate import OneOf


class TaskForm(Schema):
    id = fields.Integer(required=False)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    status = fields.Str(validate=OneOf(['To Do', 'In Progress', 'Review', 'Done']))
