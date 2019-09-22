#!/usr/bin/env python3

from flask import Blueprint
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate, MigrateCommand
from flask_restplus import Api, Namespace
from flask_script import Manager
import os
import unittest

from src import create_app, db, ma
from src.controllers import api as api_ns
from src.services import add_


blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='ASAPP Challenge Project',
          version='1.0',
          description='REST API for a chat backend'
          )

api.add_namespace(api_ns, path='/')

app = create_app(os.getenv('APP_ENV') or 'dev')
ma = Marshmallow(app)
app.register_blueprint(blueprint)

app.app_context().push()

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

add_()


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
