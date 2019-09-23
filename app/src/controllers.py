import datetime
from flask import request
from flask_restplus import Namespace, Resource, marshal_with
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs
from .dto import MainApi
from .models import User, Message, Text, Image, Video

api = MainApi.api


@api.route('createUser')
class UserRegistration(Resource):

    @api.response(200, 'Create a user in the system.')
    @api.doc('createUser')
    @api.expect(MainApi.user, validate=True)
    def post(self):
        """Creates a new User """
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            new_user = User(username=data['username'], password=data['password']).save()
            response_object = {'id': new_user.id}
            return response_object, 200
        else:
            response_object = {'status': 'fail', 'message': 'User already exists. Please Log in.'}
            return response_object, 409


@api.route('sendMessage')
class MessageCreation(Resource):

    @api.response(200, 'Send a message from one user to another.')
    @api.doc('sendMessage')
    @api.expect(MainApi.message, validate=True)
    def post(self):
        data = request.json
        type_mapping = {'text': Text, 'image': Image, 'video': Video}
        content_type = data['content']['type']
        content = type_mapping[content_type](**data['content'])
        new_message = Message(
            sender_id=data['sender'],
            recipient_id=data['recipient'],
            sent_on=datetime.datetime.utcnow(),
            content=content,
        ).save()

        response_object = {
            'id': new_message.id,
            'timestamp': new_message.sent_on.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        return response_object, 200


@api.route('getMessages')
class Messages(Resource):

    args = {
        'recipient': fields.Int(required=True),
        'start': fields.Int(required=True),
        'limit': fields.Int(missing=100),
    }

    @api.response(200, 'Fetch all existing messages to a given recipient, within a range of message IDs.')
    @api.doc('getMessages')
    @use_args(args)
    @marshal_with(MainApi.messages)
    def get(self, args):
        messages = Message.get_messages(args['recipient'], args['start'], args['limit'])
        return {'messages': messages}

