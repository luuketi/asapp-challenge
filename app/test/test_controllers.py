import json

from test.base import BaseTestCase


class CreateUserTest(BaseTestCase):

    def test_CreateUser(self):
        response = self._create_user()
        self.assert200(response)
        self.assertEqual(response.json, {'id': 1})

    def test_CreateSameUserTwice_FailAsDuplicated(self):
        response = self._create_user()
        self.assert200(response)
        self.assertEqual(response.json, {'id': 1})

        response = self._create_user()
        self.assert_status(response, 409)

    def test_CreateTwoUsers_IdsSouldIncrease(self):
        response = self._create_user({'username': 'John', 'password': '123456'})
        self.assertEqual(response.json, {'id': 1})

        response = self._create_user({'username': 'Juan', 'password': '123456'})
        self.assertEqual(response.json, {'id': 2})

    def test_BadRequests(self):
        response = self._create_user({'password': '123456'})
        self.assert400(response)

        response = self._create_user({'username': 'Juan'})
        self.assert400(response)


class LoginTest(BaseTestCase):

    def test_Login(self):
        self._create_user()
        response = self._login()
        self.assert200(response)
        self.assertEqual(response.json['id'], 1)
        self.assertTrue(response.json['token'])

    def test_WrongPassword(self):
        self._create_user({'username': 'Carl', 'password': '123456'})
        response = self._login({'username': 'Carl', 'password': '123'})
        self.assert401(response)

    def test_LoginNonCreatedUser(self):
        self._create_user()
        response = self._login({'username': 'Carl', 'password': '123'})
        self.assert401(response)

class TestLogout(BaseTestCase):

    def test_Logout(self):
        self._create_user()
        response = self._login()
        response = self._logout(response.json['token'])
        self.assert200(response)

