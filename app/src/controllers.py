from flask import request
from flask_restplus import Namespace, Resource, marshal_with
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs
from .dto import MainApi
from .services import save_new_user, save_new_message, get_messages

api = MainApi.api


@api.route('createUser')
class User(Resource):

    @api.response(200, 'Create a user in the system.')
    @api.doc('createUser')
    @api.expect(MainApi.user, validate=True)
    def post(self):
        """Creates a new User """
        data = request.json
        return save_new_user(data=data)


@api.route('sendMessage')
class Message(Resource):

    @api.response(200, 'Send a message from one user to another.')
    @api.doc('sendMessage')
    @api.expect(MainApi.message, validate=True)
    def post(self):
        data = request.json
        return save_new_message(data=data)


@api.route('getMessages')
class Messages(Resource):

    args = {
        'recipient': fields.Int(required=True),
        'start': fields.Int(required=True),
        'limit': fields.Int(missing=100),
    }

    @api.response(200, 'Fetch all existing messages to a given recipient, within a range of message IDs.')
    @api.doc('getMessages')
    @use_kwargs(args)
    @marshal_with(MainApi.messages)
    def get(self, recipient, start, limit):
        messages = get_messages(recipient, start, limit)
        return { 'messages' : messages }

        # save_new_message(data=data)


