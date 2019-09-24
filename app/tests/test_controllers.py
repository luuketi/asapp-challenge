import datetime

from tests.base import BaseTestCase


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
        self.assert_status(response, 422)

        response = self._create_user({'username': 'Juan'})
        self.assert_status(response, 422)

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


class TestSendMessage(BaseTestCase):

    def setUp(self):
        super().setUp()
        self._create_user()
        self.token = self._login().json['token']

    def tearDown(self):
        super().tearDown()

    def test_SendTextMessage(self):
        data = {'sender': 1, 'recipient': 1, 'content': {'type': 'text', 'text': 'hola'}}
        response = self._post(self._messages_url, data, self.token)
        self.assertEqual(response.json['id'], 1)
        self.assertIn(str(datetime.datetime.utcnow().date()), response.json['timestamp'])

    def test_SendWrongTypeContent(self):
        data = {'sender': 1, 'recipient': 1, 'content': {'type': 'audio', 'text': 'hola'}}
        response = self._post(self._messages_url, data, self.token)
        self.assert_status(response, 422)

    def test_SendTextMessageWithoutText(self):
        data = {'sender': 1, 'recipient': 1, 'content': {'type': 'text'}}
        response = self._post(self._messages_url, data, self.token)
        self.assert_status(response, 422)

    def test_SendImageMessage(self):
        data = {'sender': 1, 'recipient': 1, 'content': {'type': 'image', 'url': 'web.co', 'height': 800, 'width': 600}}
        response = self._post(self._messages_url, data, self.token)
        self.assertEqual(response.json['id'], 1)
        self.assertIn(str(datetime.datetime.utcnow().date()), response.json['timestamp'])

    def test_SendVideoMessage(self):
        data = {'sender': 1, 'recipient': 1, 'content': {'type': 'video', 'url': 'web.com', 'source': 'youtube'}}
        response = self._post(self._messages_url, data, self.token)
        self.assertEqual(response.json['id'], 1)
        self.assertIn(str(datetime.datetime.utcnow().date()), response.json['timestamp'])

    def test_SendVideoMessageWithWrongSource(self):
        data = {'sender': 1, 'recipient': 1, 'content': {'type': 'video', 'url': 'web.com', 'source': 'youtubee'}}
        response = self._post(self._messages_url, data, self.token)
        self.assert_status(response, 422)

    def test_WrongSender(self):
        data = {'sender': 10, 'recipient': 1, 'content': {'type': 'video', 'url': 'web.com', 'source': 'youtube'}}
        response = self._post(self._messages_url, data, self.token)
        self.assert400(response)

    def test_WrongRecipient(self):
        data = {'sender': 1, 'recipient': 10, 'content': {'type': 'video', 'url': 'web.com', 'source': 'youtube'}}
        response = self._post(self._messages_url, data, self.token)
        self.assert400(response)

    def test_NoAuthInMessage(self):
        data = {'sender': 1, 'recipient': 1, 'content': {'type': 'image', 'url': 'web.co', 'height': 8, 'width': 6}}
        response = self._post(self._messages_url, data)
        self.assert401(response)


class TestMessages(BaseTestCase):

    def setUp(self):
        super().setUp()
        for i in range(6):
            self._create_user({'username': 'user{}'.format(i), 'password': '123456'})
        self.token = self._login({'username': 'user1', 'password': '123456'}).json['token']

    def test_GetMessages(self):
        data = {'sender': 1, 'recipient': 1, 'content': {'type': 'image', 'url': 'web.co', 'height': 8, 'width': 6}}
        self._post(self._messages_url, data, self.token)
        response = self._get(self._messages_url, {'recipient': 1, 'start': 1}, self.token)
        response_json = response.json['messages'][0]
        self.assert200(response)
        self.assertEqual(data['sender'], response_json['sender'])
        self.assertEqual(data['recipient'], response_json['recipient'])
        self.assertDictEqual(data['content'], response_json['content'])

    def test_GetMultipleMessages(self):
        for s in range(1, 4):
            for r in range(1, 3):
                for i in range(6):
                    data = {'sender': s, 'recipient': r,
                            'content': {'type': 'image', 'url': 'web.co', 'height': i, 'width': 6}}
                    self._post(self._messages_url, data, self.token)
        response = self._get(self._messages_url, {'recipient': 2, 'start': 1}, self.token)
        self.assert200(response)
        self.assertEqual(len(response.json['messages']), 18)

    def test_GetMessagesWithHigherStartAndLimit(self):
        for i in range(15):
            data = {'sender': 1, 'recipient': 1, 'content': {'type': 'image', 'url': 'web.co', 'height': i, 'width': 6}}
            self._post(self._messages_url, data, self.token)
        response = self._get(self._messages_url, {'recipient': 1, 'start': 10, 'limit': 2}, self.token)
        self.assert200(response)
        self.assertEqual(len(response.json['messages']), 2)
        self.assertEqual(response.json['messages'][0]['id'], 10)

    def test_NoAuthInGetMessages(self):
        data = {'sender': 1, 'recipient': 1, 'content': {'type': 'image', 'url': 'web.co', 'height': 8, 'width': 6}}
        self._post(self._messages_url, data, self.token)
        response = self._get(self._messages_url, {'recipient': 1, 'start': 1})
        self.assert401(response)

