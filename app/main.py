#!/usr/bin/env python3

from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import os
import unittest

from src import create_app, db
from src.controllers import blueprint
import src.models as models

app = create_app(os.getenv('APP_ENV') or 'dev')
app.register_blueprint(blueprint)
app.app_context().push()

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

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
