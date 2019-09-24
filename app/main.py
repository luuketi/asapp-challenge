#!/usr/bin/env python3

from flask import Blueprint
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, MigrateCommand
from flask_restplus import Api
from flask_script import Manager
import os
import unittest

from src import create_app, db
from src.controllers import api as api_ns
import src.models as models


blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='ASAPP Challenge Project',
          version='1.0',
          description='REST API for a chat backend'
          )

api.add_namespace(api_ns, path='/v1')

app = create_app(os.getenv('APP_ENV') or 'dev')
app.register_blueprint(blueprint)
app.app_context().push()

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']


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
