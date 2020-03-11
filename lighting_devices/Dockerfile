FROM python:3
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY run_devices.py /usr/src/app
COPY config.py /usr/src/app
RUN mkdir -p /usr/src/app/lighting_devices
COPY __init__.py /usr/src/app/lighting_devices
COPY bulb.py /usr/src/app/lighting_devices
COPY bulb_iot.py /usr/src/app/lighting_devices
CMD ["python", "./run_devices.py"]

