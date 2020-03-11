from flask import current_app

from web_app.api import bp
from flask import jsonify

from web_app import mqtt_client
from web_app.models import Device


@bp.route('/devices', methods=['GET'])
def devices():
    all_devices = Device.query.all()
    return jsonify([dev.serialize for dev in all_devices])

@bp.route('/device/<string:dev_name>/set/<string:light>', methods=['POST'])
def set_light(dev_name, light):
    """
    set light for device
    :param dev_name:
    :param light:
    :return:
    """
    find_device = Device.query.filter_by(name=dev_name).first()

    if find_device and light in ['on', 'off']:
        mqtt_client.publish(topic=f'home/light/{find_device.name}/light/set', payload=light, qos=2)
        return jsonify({'MSG':'OK'}),200
    else:
        return 400
# @mqtt.on_message()
# def register_device(client, userdata, message):
#     print('asfsa')
#     """
#     Register device in DB
#     :param client:
#     :param userdata:
#     :param message:
#     :return:
#     """
#     device_name = message.payload.decode("utf-8")
#     with current_app.app_context():
#         # find device in db, if not exists add to db
#         find_model = Device.query.filter_by(name=device_name).first()
#         if find_model is None:
#             device = Device(name=device_name, status='on')
#             try:
#                 db.session.add(device_name)
#                 db.session.commit()
#             except:
#                 db.session.rollback()
#
#
# @mqtt.on_log()
# def handle_logging(client, userdata, level, buf):
#
#         print(buf)