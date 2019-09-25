
from flask import Flask, Blueprint
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

from src.config import config_by_name


db = SQLAlchemy()
blueprint = Blueprint('api', __name__)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    flask_bcrypt = Bcrypt()
    app.register_blueprint(blueprint)
    app.app_context().push()
    migrate = Migrate(app, db)

    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    return app, manager
