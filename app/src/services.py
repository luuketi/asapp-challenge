import datetime
from . import db
from .models import User, Message, Text, Image, Video


def add_():
    #u=User(username='b',password='b')
    #db.session.add(u)
    #db.session.commit()
    pass
    c = Text(type='text', text='hola')
    db.session.add(c)
    cid = db.session.commit()

    m = Message(sent_on=datetime.datetime.utcnow(), sender_id=1, recipient_id=1, content_id=2)
    db.session.add(m)
    cid = db.session.commit()


