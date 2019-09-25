#!/usr/bin/env python3

from flask_jwt_extended import JWTManager
import os
import unittest

from src import create_app, db
from src.controllers import blueprint
import src.models as models

app, manager = create_app(os.getenv('APP_ENV') or 'dev')
jwt = JWTManager(app)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedToken.is_jti_blacklisted(jti)


@app.before_first_request
def create_tables():
    db.create_all()


@manager.command
def run():
    app.run(port=8080)


@manager.command
def test():
    tests = unittest.TestLoader().discover('tests', pattern='*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    manager.run()
