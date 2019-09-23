import datetime
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_raw_jwt
from flask_restplus import Resource, marshal_with
from webargs import fields
from webargs.flaskparser import use_args
from src import db
from src.dto import MainApi
from src.models import User, Message, Text, Image, Video, RevokedToken

api = MainApi.api


@api.route('/users')
class Users(Resource):

    @api.response(200, '')
    @api.response(409, 'User already exists.')
    @api.doc('createUser')
    @api.expect(MainApi.user, validate=True)
    def post(self):
        """Create a user in the system."""
        data = request.json

        # checks if user exists
        if User.find_by_username(data['username']):
            return {'status': 'fail', 'message': 'User already exists. Please Log in.'}, 409

        # create user
        new_user = User(username=data['username'], password=data['password']).save()
        return {'id': new_user.id}, 200


@api.route('/login')
class Login(Resource):

    @api.response(200, '')
    @api.response(401, 'Unauthorized')
    @api.expect(MainApi.user, validate=True)
    def post(self):
        """Log in as an existing user."""
        data = request.json

        # check if user exists
        current_user = User.find_by_username(data['username'])
        if not current_user:
            return {'status': 'fail', 'message': "User {} doesn't exist".format(data['username'])}, 401

        # return token if password matches
        if current_user.check_password(data['password']):
            access_token = create_access_token(identity=data['username'])
            return {'id': current_user.id, 'token': access_token}
        else:
            return {'status': 'fail', 'message': 'Wrong credentials'}, 401


@api.route('/logout')
class Logout(Resource):

    @jwt_required
    def post(self):
        """Log out an existing user."""
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.save()
            return {'message': 'Access token has been revoked'}
        except Exception:
            return {'status': 'fail', 'message': 'Something went wrong'}, 500


@api.route('/messages')
class Messages(Resource):

    def _check_user_exists(self, user_type, user_id):
        if not User.query.filter_by(id=user_id).first():
            return {'status': 'fail', 'message': "{} {} doesn't exist".format(user_type, user_id)}, 400

    @api.response(200, '')
    @api.response(400, 'Sender/Receiver not found')
    @api.doc('sendMessage')
    @api.expect(MainApi.message, validate=True)
    @jwt_required
    def post(self):
        """Send a message from one user to another."""
        data = request.json

        # checks if sender and recipient exist
        user_err = self._check_user_exists('sender', data['sender'])
        recipient_err = self._check_user_exists('recipient', data['recipient'])
        if user_err or recipient_err:
            return user_err or recipient_err

        # create content object
        type_mapping = {'text': Text, 'image': Image, 'video': Video}
        content_type = data['content']['type']
        try:
            content = type_mapping[content_type](**data['content'])
        except Exception as e:
            return {'status': 'fail', 'message': str(e.args[0])}, 500

        new_message = Message(
            sender_id=data['sender'],
            recipient_id=data['recipient'],
            sent_on=datetime.datetime.utcnow(),
            content=content,
        ).save()

        return {'id': new_message.id, 'timestamp': new_message.sent_on.strftime("%Y-%m-%dT%H:%M:%SZ")}, 200

    args = {
        'recipient': fields.Int(required=True),
        'start': fields.Int(required=True),
        'limit': fields.Int(missing=100),
    }

    @api.response(200, '')
    @api.doc('getMessages')
    @use_args(args)
    @marshal_with(MainApi.messages)
    @jwt_required
    def get(self, args):
        """Fetch all existing messages to a given recipient, within a range of message IDs."""
        messages = Message.get_messages(args['recipient'], args['start'], args['limit'])
        return {'messages': messages}


@api.route('/check')
class Check(Resource):

    @api.response(200, '')
    def post(self):
        """Check the health of the system."""
        if self.query_health() != 1:
            raise Exception('unexpected query result')
        return {"health": "ok"}, 200

    def query_health(self):
        with db.engine.connect() as conn:
            result = conn.execute("SELECT 1")
            (res,) = result.fetchone()
            return res
