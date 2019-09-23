
from flask_testing import TestCase
import json
from asapp.app.main import app
from app.main import db

class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        app.config.from_object('app.main.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()



class CreateUserTest(BaseTestCase):

    def create_user(self):
        return self.client.post(
            '/createUser/',
            data=json.dumps(dict(
                username='username',
                password='123456'
            )),
            content_type='application/json'
        )

