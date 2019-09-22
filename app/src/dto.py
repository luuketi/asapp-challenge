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
    api = Namespace('api', description='object descriptions')
    user = api.model('user', {
        'username': fields.String(required=True),
        'password': fields.String(required=True),
    })

    content = api.model('content', {
        'type': fields.String,
        'class': fields.String(discriminator=True),
    })

    text = api.inherit('text', content, {
        'text': fields.String
    })

    image = api.inherit('image', content, {
        'url': fields.Url,
        'height': fields.Integer,
        'width': fields.Integer,
    })

    video = api.inherit('video', content, {
        'url': fields.Url,
        'source': fields.String(enum=Source._member_names_)
    })

    mapping = {Text: text, Image: image, Video: video}

    message = api.model('message', {
        'sender': fields.Integer(required=True),
        'recipient': fields.Integer(required=True),
        'content': fields.Polymorph(mapping, required=True),
    })

