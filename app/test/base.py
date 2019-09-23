
from flask_testing import TestCase
import json
from main import app, db


class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        app.config.from_object('src.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _post(self, route, data, token=None):
        headers = {'Authorization': 'Bearer ' + token} if token else {}
        return self.client.post(
            route,
            content_type='application/json',
            headers=headers,
            data=json.dumps(data),
        )

    def _create_user(self, data=None):
        data = {'username': 'John', 'password': '123456'} if not data else data
        return self._post('/createUser', data)

    def _login(self, data=None):
        data = {'username': 'John', 'password': '123456'} if not data else data
        return self._post('/login', data)

    def _logout(self, token, data=None):
        data = {'username': 'John', 'password': '123456'} if not data else data
        return self._post('/logout', data, token)


