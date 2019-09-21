import uuid
import datetime

from . import db
from .models import User


def save_new_user(data):
    user = User.query.filter_by(email=data['username']).first()
    if not user:
        new_user = User(
            username=data['username'],
            password=data['password'],
            registered_on=datetime.datetime.utcnow(),
        )
        user_id = save_changes(new_user)
        response_object = {
            'id': user_id,
        }
        return response_object, 200
    else:
        response_object = {
            'status': 'fail',
            'message': 'User already exists. Please Log in.',
        }
        return response_object, 409


def get_all_users():
    return User.query.all()


def get_a_user(public_id):
    return User.query.filter_by(public_id=public_id).first()


def save_changes(data):
    db.session.add(data)
    db.session.commit()
    return data.id
