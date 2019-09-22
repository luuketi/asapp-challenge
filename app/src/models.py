import enum
from . import db
import flask_bcrypt
from sqlalchemy import Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class User(db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)


    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = flask_bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return flask_bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User '{}'>".format(self.username)


class Content(Base):
    __tablename__ = "content"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(15), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity' : 'content',
        'polymorphic_on' : type,
    }


class Text(Content):
    __tablename__ = 'text'

    id = db.Column(db.Integer, db.ForeignKey('content.id'), primary_key=True)
    text = db.Column(db.String, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity' : 'text',
    }


class Image(Content):
    __tablename__ = 'image'

    id = db.Column(db.Integer, db.ForeignKey('content.id'), primary_key=True)
    url = db.Column(db.String, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity' : 'image',
    }


class Source(enum.Enum):
    youtube = 1
    vimeo   = 2


class Video(Content):
    __tablename__ = 'video'

    id = db.Column(db.Integer, db.ForeignKey('content.id'), primary_key=True)
    url = db.Column(db.String, nullable=False)
    source = db.Column(Enum(Source), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity' : 'video',
    }


class Message(db.Model):

    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = relationship("MessageSender")

    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient = relationship("MessageRecipient")

    content_id = db.Column(db.Integer, db.ForeignKey('content.id'))
    content = relationship("MessageContent")

    def __repr__(self):
        return "<User '{}'>".format(self.username)


