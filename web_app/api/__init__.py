from flask import Blueprint

# api blueprint
bp = Blueprint('api', __name__)

from web_app.api import api
from web_app.api import mqtt_handlers
