from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_mqtt import Mqtt

# db and migrate definition
db = SQLAlchemy()
migrate = Migrate()
mqtt = Mqtt()


def create_app(config_class=Config):
    """Creates and return flask app"""

    # new flask app from config
    app = Flask(__name__)
    app.config.from_object(config_class)

    ## logger


    # db, migrate init
    db.init_app(app)
    migrate.init_app(app, db)

    # mqtt init
    mqtt.init_app(app)

    # register main blueprint
    from web_app.api import bp as api_bp
    app.register_blueprint(api_bp)

    return app
