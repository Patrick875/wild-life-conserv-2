from marshmallow import Schema,fields,validate

class FeedbackSchema(Schema):
    warning_id=fields.Integer(required=True)
    message=fields.String(required=True,validate=validate.Length(min=3))