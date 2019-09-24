import enum
import flask_bcrypt
from sqlalchemy.orm import relationship, validates

from src import db


class SaveMixin:
    __table_args__ = {'extend_existing': True}

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self


class User(db.Model, SaveMixin):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = flask_bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return flask_bcrypt.check_password_hash(self.password_hash, password)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first()

    def __repr__(self):
        return "<User '{}'>".format(self.username)


class RevokedToken(db.Model, SaveMixin):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class Content(db.Model, SaveMixin):
    __tablename__ = "content"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(15), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'content',
        'polymorphic_on': type,
    }


class Text(Content):
    __tablename__ = 'text'

    id = db.Column(db.Integer, db.ForeignKey('content.id'), primary_key=True)
    text = db.Column(db.String, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'text',
    }

    def __repr__(self):
        return "<Text '{}'>".format(self.text)


class Image(Content):
    __tablename__ = 'image'

    id = db.Column(db.Integer, db.ForeignKey('content.id'), primary_key=True)
    url = db.Column(db.String, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'image',
    }

    def __repr__(self):
        return "<Image {}x{} in {}>".format(self.height, self.width, self.url)


class Source(enum.Enum):
    youtube = 1
    vimeo   = 2


class Video(Content):
    __tablename__ = 'video'

    id = db.Column(db.Integer, db.ForeignKey('content.id'), primary_key=True)
    url = db.Column(db.String, nullable=False)
    source = db.Column(db.Enum(Source), nullable=False)

    @validates('source')
    def validate_source(self, key, source):
        assert source in Source._member_names_, '{} is not a valid source'.format(source)
        return source

    __mapper_args__ = {
        'polymorphic_identity': 'video',
    }

    def __repr__(self):
        return "<Image in {} {}>".format(self.source, self.url)


class Message(db.Model, SaveMixin):

    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False)

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = relationship("User", foreign_keys=[sender_id])

    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient = relationship("User", foreign_keys=[recipient_id])

    content_id = db.Column(db.Integer, db.ForeignKey('content.id'))
    content = relationship("Content", foreign_keys=[content_id])

    @classmethod
    def get_messages(cls, recipient_id, start, limit):
        messages = Message.query.filter(Message.recipient_id == recipient_id,
                                        Message.id >= start
                                        ).limit(limit).all()

        return messages

    def __repr__(self):
        return "<Message {} {} {}>".format(self.sender, self.recipient, self.content)
