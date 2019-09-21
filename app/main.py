#!/usr/bin/env python3

from flask import Blueprint
from flask_migrate import Migrate, MigrateCommand
from flask_restplus import Api
from flask_script import Manager
import os
import unittest


from src import create_app, db
from src.controllers import api as user_ns
from src.models import User


blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='ASAPP Challenge Project',
          version='1.0',
          description='REST API for a chat backend'
          )

api.add_namespace(user_ns, path='/users')

app = create_app(os.getenv('APP_ENV') or 'dev')
app.register_blueprint(blueprint)

app.app_context().push()

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def run():
    app.run(port=8080)


@manager.command
def test():
    tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    manager.run()
