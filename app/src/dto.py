from flask_restplus import Namespace, fields
from .models import User, Source, Text, Image, Video
from . import ma



'''
class UserSchema(ma.ModelSchema):
    class Meta:
        model = User


class BookSchema(ma.TableSchema):
    class Meta:
        table = Book.__table__

'''


class MainApi:

    class Date(fields.Raw):
        def format(self, value):
            return value.strftime("%Y-%m-%dT%H:%M:%SZ")

    api = Namespace('api', description='object descriptions')
    user = api.model('user', {
        'username': fields.String(required=True),
        'password': fields.String(required=True),
    })

    content = api.model('content', {
        'type': fields.String(required=True, discriminator=True),
    })

    text = api.inherit('text', content, {
        'text': fields.String(required=True),
    })

    image = api.inherit('image', content, {
        'url': fields.Url(required=True),
        'height': fields.Integer(required=True),
        'width': fields.Integer(required=True),
    })

    video = api.inherit('video', content, {
        'url': fields.String(required=True),
        'source': fields.String(required=True, attribute=lambda x: str(Source(x.source).name))
    })

    mapping = {Text: text, Image: image, Video: video}

    message = api.model('message', {
        'id': fields.Integer,
        'timestamp': Date(attribute='sent_on'),
        'sender': fields.Integer(required=True, attribute='sender.id'),
        'recipient': fields.Integer(required=True, attribute='recipient.id'),
        'content': fields.Polymorph(mapping, required=True),
    })

    messages = {
        'messages': (fields.List(fields.Nested(message)))
    }


