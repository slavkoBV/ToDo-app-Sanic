from marshmallow import Schema, fields
from marshmallow.validate import OneOf


class TaskForm(Schema):
    id = fields.Integer(required=False)
    title = fields.String(required=True)
    description = fields.String(required=True)
    status = fields.String(validate=OneOf(['To Do', 'In Progress', 'Review', 'Done']), required=True)


class TaskUpdateForm(Schema):
    title = fields.String(required=False)
    description = fields.String(required=False)
    status = fields.String(validate=OneOf(['To Do', 'In Progress', 'Review', 'Done']), required=False)
