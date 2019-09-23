import datetime
from flask import request
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from flask_restplus import Namespace, Resource, marshal_with
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs
from .dto import MainApi
from .models import User, Message, Text, Image, Video, RevokedToken

api = MainApi.api


@api.route('createUser')
class SignUp(Resource):

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


@api.route('login')
class Login(Resource):

    @api.response(200, 'Create a user in the system.')
    @api.expect(MainApi.user, validate=True)
    def post(self):
        data = request.json
        current_user = User.find_by_username(data['username'])

        if not current_user:
            return {'message': "User {} doesn't exist".format(data['username'])}

        if current_user.check_password(data['password']):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'id': current_user.id,
                'token': access_token,
            }
        else:
            return {'message': 'Wrong credentials'}


@api.route('logout')
class Logout(Resource):

    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.save()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500



@api.route('sendMessage')
class MessageCreation(Resource):

    @api.response(200, 'Send a message from one user to another.')
    @api.doc('sendMessage')
    @api.expect(MainApi.message, validate=True)
    @jwt_required
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
    @jwt_required
    def get(self, args):
        messages = Message.get_messages(args['recipient'], args['start'], args['limit'])
        return {'messages': messages}

