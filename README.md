### Installing
```
docker-compose build
docker-compose up -d
```
### ALL devices
```
GET http://0.0.0.0:5000/devices
```
### Switch light
```
POST localhost:5000/device/<device_name>/set/<on/off>
eg. localhost:5000/device/Kitchen/set/off
```
### console app
```
GET client_app.py
```
