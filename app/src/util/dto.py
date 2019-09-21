from flask_restplus import Namespace, fields


class UserDto:
    api = Namespace('user', description='user related operations')
    user = api.model('user', {
        'username': fields.String(required=True),
        'password': fields.String(required=True),
    })


class MessageDto:
    api = Namespace('message', description='message operations')
    content = api.model('content', {
        'type': fields.String,
        'text': fields.String,
    })
    user = api.model('message', {
        'sender': fields.String(required=True),
        'recipient': fields.String(required=True),
        'content': fields.Nested(content, required=True),
    })

