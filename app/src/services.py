import uuid
import datetime

from . import db
from .models import User, Message, Content, Text, Image, Video


def save_new_user(data):
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        new_user = User(
            username=data['username'],
            password=data['password'],
            registered_on=datetime.datetime.utcnow(),
        )
        user_row = save_changes(new_user)
        response_object = {
            'id': user_row.id,
        }
        return response_object, 200
    else:
        response_object = {
            'status': 'fail',
            'message': 'User already exists. Please Log in.',
        }
        return response_object, 409


def save_new_message(data):
    message = Message(

    )

    message.sent_on = datetime.datetime.utcnow()

    message_row = save_changes(message)
    response_object = {
        'id': message_row.id,
        'timestamp': message_row.sent_on
    }
    return response_object, 200


def get_messages(recipient_id, start, limit):
    messages = Message.query.filter(Message.recipient_id == recipient_id,
                                    Message.id >= start
                                   ).limit(limit).all()

    print(messages)

    return messages


def save_changes(data):
    db.session.add(data)
    db.session.commit()
    return data


def add_():
    #u=User(username='b',password='b')
    #db.session.add(u)
    #db.session.commit()

    c = Text(type='text', text='hola')
    db.session.add(c)
    cid = db.session.commit()

    m = Message(sent_on=datetime.datetime.utcnow(), sender_id=1, recipient_id=1, content_id=2)
    db.session.add(m)
    cid = db.session.commit()


