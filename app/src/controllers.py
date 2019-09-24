import datetime
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt
from flask_restplus import Resource, Namespace
from webargs import fields
from webargs.flaskparser import use_args, use_kwargs
from src import db
from src.dto import *
from src.models import User, Message, Text, Image, Video, RevokedToken

api = Namespace('api', description='object descriptions')


@api.route('/users')
class Users(Resource):

    @api.response(200, '')
    @api.response(409, 'User already exists.')
    @api.doc('createUser')
    @use_kwargs(UserSchema())
    def post(self, username, password):
        """Create a user in the system."""

        # checks if user exists
        if User.find_by_username(username):
            return {'status': 'fail', 'message': 'User already exists. Please Log in.'}, 409

        # create user
        new_user = User(username=username, password=password).save()
        return {'id': new_user.id}, 200


@api.route('/login')
class Login(Resource):

    @api.response(200, '')
    @api.response(401, 'Unauthorized')
    @use_kwargs(UserSchema())
    def post(self, username, password):
        """Log in as an existing user."""

        # check if user exists
        current_user = User.find_by_username(username)
        if not current_user:
            return {'status': 'fail', 'message': "User {} doesn't exist".format(username)}, 401

        # return token if password matches
        if current_user.check_password(password):
            access_token = create_access_token(identity=username)
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
        if not User.find_by_id(user_id):
            return {'status': 'fail', 'message': "{} {} doesn't exist".format(user_type, user_id)}, 400

    @api.response(200, '')
    @api.response(400, 'Sender/Receiver not found')
    @api.doc('sendMessage')
    @use_args(MessageSchema())
    @jwt_required
    def post(self, message):
        """Send a message from one user to another."""

        # checks if sender and recipient exist
        sender_err = self._check_user_exists('sender', message.sender)
        recipient_err = self._check_user_exists('recipient', message.recipient)
        if sender_err or recipient_err:
            return sender_err or recipient_err

        new_message = Message(
            sender_id=message.sender,
            recipient_id=message.recipient,
            timestamp=datetime.datetime.utcnow(),
            content=message.content,
        ).save()

        return {'id': new_message.id, 'timestamp': new_message.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")}, 200

    args = {
        'recipient': fields.Int(required=True),
        'start': fields.Int(required=True),
        'limit': fields.Int(missing=100),
    }

    @api.response(200, '')
    @api.doc('getMessages')
    @use_kwargs(args)
    @jwt_required
    def get(self, recipient, start, limit):
        """Fetch all existing messages to a given recipient, within a range of message IDs."""
        messages = Message.get_messages(recipient, start, limit)
        return MessagesSchema().dump({'messages': messages})


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
