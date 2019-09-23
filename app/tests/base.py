from flask import url_for
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
        self._messages_url = url_for('api.api_messages')


    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _get(self, route, params, token=None):
        headers = {'Authorization': 'Bearer ' + token} if token else {}
        return self.client.get(
            route,
            query_string=params,
            content_type='application/json',
            headers=headers,
        )

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
        return self._post(url_for('api.api_users'), data)

    def _login(self, data=None):
        data = {'username': 'John', 'password': '123456'} if not data else data
        return self._post(url_for('api.api_login'), data)

    def _logout(self, token, data=None):
        data = {'username': 'John', 'password': '123456'} if not data else data
        return self._post(url_for('api.api_logout'), data, token)


