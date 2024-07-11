from server.ble.ble_server import server

def get_characteristic_by_uuid():
    print('Get char')
    return server.get_characteristic("51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B")