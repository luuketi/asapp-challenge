from marshmallow import Schema, fields, post_load, validate

from src.models import Source, Text, Image, Video, Message
from marshmallow_oneofschema import OneOfSchema


class UserSchema(Schema):
    username = fields.String(required=True, validate=[ validate.Length(min=1, error="Please enter your user name.")])
    password = fields.String(required=True)


class TextSchema(Schema):
    text = fields.String(required=True)

    @post_load
    def make(self, data, **kwargs):
        return Text(**data)


class ImageSchema(Schema):
    url = fields.String(required=True)
    height = fields.Integer(required=True)
    width = fields.Integer(required=True)

    @post_load
    def make(self, data, **kwargs):
        return Image(**data)


class VideoSchema(Schema):
    url = fields.String(required=True)
    source = fields.String(required=True, validate=validate.OneOf(Source._member_names_))

    @post_load
    def make(self, data, **kwargs):
        return Video(**data)


class ContentSchema(OneOfSchema):
    type = fields.String(required=True)

    type_schemas = {"text": TextSchema, "image": ImageSchema, 'video': VideoSchema}
    obj_types = {Text: 'text', Image: 'image', Video: 'video'}

    def get_obj_type(self, obj):
        for o, t in self.obj_types.items():
            if isinstance(obj, o):
                return t
        raise Exception("Unknown object type: {}".format(obj.__class__.__name__))


class MessageSchema(Schema):
    id = fields.Integer(dump_only=True)
    timestamp = fields.Date("%Y-%m-%dT%H:%M:%SZ", dump_only=True)
    sender = fields.Method("_get_sender", deserialize="_load_sender", required=True)
    recipient = fields.Method("_get_recipient", deserialize="_load_sender", required=True)
    content = fields.Nested(ContentSchema, required=True)

    def _get_sender(self, obj):
        return int(obj.sender.id)

    def _load_sender(self, value):
        return int(value)

    def _get_recipient(self, obj):
        return int(obj.recipient.id)

    def _load_recipient(self, value):
        return int(value)

    @post_load
    def make(self, data, **kwargs):
        return Message(**data)


class MessagesSchema(Schema):
    messages = fields.Nested(MessageSchema, many=True)

