import sys
import requests
import urllib.parse


def try_connect(addres_api):
    """
    Validate connection
    :param addres_api:
    :return:
    """

    # try connect to index
    try:
        response = requests.get(address_api)
    except Exception as E:
        # if not response exit
        print(E)
        return False

    # if not working, exit
    if response.status_code != 200:
        return False

    # ok
    return True


def pprint_options():
    data = """What do you want to do?
    1. Show all devices
    2. Switch light
    q for quit"""
    print(data)


def check_input(opt):
    """Check input if is 1 or 2"""
    if len(opt)!=1:
        return False
    try:
        opt = int(opt)
    except:
        return False

    if opt !=1 and opt!=2:
        return False

    return opt


def get_devices(api_address):
    """
    print all devices and status
    :param api_address:
    :return:
    """
    address = urllib.parse.urljoin(api_address, 'devices')
    try:
        response = requests.get(address)
    except Exception as e:
        print('Got exception, not answering')

    if response.status_code != 200:
        print("Something wrong, not answering")
    else:
        msg = response.json()

        if len(msg) == 0:
            print("No devices")
        else:
            for dev in msg:
                print(f"Device: {dev['name']} light {dev['light']} status {dev['status']}")


def switch_light(api_address):
    """Switch light"""

    # todo validates user inputs
    print('Enter device name')
    device_name = input()

    print('Light on or off?')
    light = input()
    if len(device_name) < 1 or light not in ['on', 'off']:
        print('Wrong device name or command')
        return
    address = urllib.parse.urljoin(api_address, f"device/{device_name}/set/{light}")

    try:
        response = requests.post(address)
    except Exception as e:
        print('Got exception, not answering')

    if response.status_code != 200 and response.status_code != 400:
        print("Something wrong, not answering")
    else:
        msg = response.json()
        for key, val in msg.items():
            print(f"{key}: {val}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage python client_app.py API ADDRESS')
        sys.exit()

    # todo validate address

    address_api = sys.argv[1]

    if not try_connect(address_api):
        print('Wrong api address')
        sys.exit()

    exit = False
    while not exit:
        pprint_options()
        choice = input()

        if choice == 'q':
            exit = True
        validate_opt = check_input(choice)

        if validate_opt == 1:
            get_devices(address_api)
        elif validate_opt == 2:
            switch_light(address_api)
