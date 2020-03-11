import os

class Config:
    MQTT_BROKER_URL = "127.0.0.1"
    MQTT_BROKER_PORT = 1883
    MQTT_KEEPALIVE = 5
    MQTT_CLIENT_ID = 'flask_client'
    MQTT_CLEAN_SESSION = False

    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                                  'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSONIFY_PRETTYPRINT_REGULAR = True