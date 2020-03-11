from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config
import threading

from paho.mqtt.client import MQTTv311

# db and migrate definition
db = SQLAlchemy()
migrate = Migrate()

from web_app.mqtt_client.client import FlaskMQTT
mqtt_client = FlaskMQTT(client_id='FLASK_MQTT', clean_session=Config.MQTT_CLEAN_SESSION, protocol=MQTTv311)


def create_app(config_class=Config):
    """Creates and return flask app"""

    # new flask app from config
    app = Flask(__name__)
    app.config.from_object(config_class)

    ## logger

    # db, migrate init
    db.init_app(app)
    migrate.init_app(app, db)
    mqtt_client.init_app(app)
    mqtt_client.run(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)


    # register main blueprint
    from web_app.api import bp as api_bp
    app.register_blueprint(api_bp)

    return app


# def start_mqtt(mqtt_client):
#
#     mqtt = threading.Thread(target=mqtt_client.run, args=(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE))
#     mqtt.start()

from web_app import models