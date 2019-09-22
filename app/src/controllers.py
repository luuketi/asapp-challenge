from flask import request
from flask_restplus import Namespace, Resource
from flask_restplus import Namespace, fields

from .dto import MainApi
from .services import save_new_user

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
        return save_new_user(data=data)
