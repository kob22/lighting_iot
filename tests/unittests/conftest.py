import pytest
from os.path import dirname
import os
import subprocess
from tests.paho_mqtt_testing.interoperability import mqtt
import signal
import time
from web_app import create_app, db as _db, mqtt_client


class TestConfig:

    MQTT_BROKER_URL = "127.0.0.1"
    MQTT_BROKER_PORT = 1883
    MQTT_KEEPALIVE = 5
    MQTT_CLIENT_ID = 'flask_client'
    MQTT_CLEAN_SESSION = False
    TESTING = True
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    TESTDB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_app.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + TESTDB_PATH + '?check_same_thread=False'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSONIFY_PRETTYPRINT_REGULAR = True


@pytest.fixture(scope='session')
def mqtt_broker_start():

    cmd = f"python ./tests/paho_mqtt_testing/interoperability/startbroker.py"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
    time.sleep(2)
    yield

    os.killpg(os.getpgid(p.pid), signal.SIGTERM)


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""

    app = create_app(config_class=TestConfig)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    if os.path.exists(TestConfig.TESTDB_PATH):
        os.unlink(TestConfig.TESTDB_PATH)

    def teardown():
        _db.drop_all()
        os.unlink(TestConfig.TESTDB_PATH)

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session

@pytest.fixture
def client(app):
    """Return client app"""
    return app.test_client()