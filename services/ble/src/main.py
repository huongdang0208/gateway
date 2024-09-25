import sys
import logging
import asyncio
import threading
import socket
import os
from typing import Any, Dict, Union
from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)
import hubscreen_pb2

# Constants
BLE_SOCKET_PATH = "/tmp/ble_socket"

server = BlessServer

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

trigger: Union[asyncio.Event, threading.Event]
if sys.platform in ["darwin", "win32"]:
    trigger = threading.Event()
else:
    trigger = asyncio.Event()

def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    logger.debug(f"Reading {characteristic.value}")
    return characteristic.value

def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    logger.debug(f"Writing {value} to {characteristic}")
    characteristic.value = value
    logger.debug(f"Char value set to {characteristic.value}")
    if characteristic.value == b"\x0f":
        logger.debug("Nice")
        trigger.set()

def update_ble_characteristics(command):
    """
    Updates BLE characteristics based on the received command from the master service.
    """
    for led in command.led_device:
        if led.id == "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B":  # Matching characteristic UUID
            value = b"\x01" if led.state else b"\x00"
            characteristic = server.get_characteristic(led.id)
            if characteristic:
                write_request(characteristic, value)

    for sw in command.sw_device:
        if sw.id == "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B":  # Matching characteristic UUID
            value = b"\x01" if sw.state else b"\x00"
            characteristic = server.get_characteristic(sw.id)
            if characteristic:
                write_request(characteristic, value)

async def listen_for_commands():
    """
    Listens for commands from the master service via Unix domain socket.
    """
    if os.path.exists(BLE_SOCKET_PATH):
        os.remove(BLE_SOCKET_PATH)

    server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_sock.bind(BLE_SOCKET_PATH)
    server_sock.listen(5)

    logger.info("Listening for commands from master service...")

    while True:
        client_sock, _ = server_sock.accept()
        data = client_sock.recv(1024)
        if data:
            command = hubscreen_pb2.Command()
            command.ParseFromString(data)
            logger.debug(f"Received command: {command}")
            update_ble_characteristics(command)

        client_sock.close()

async def run(loop):
    global server 
    trigger.clear()

    # Instantiate the server
    gatt: Dict = {
        "A07498CA-AD5B-474E-940D-16F1FBE7E8CD": {
            "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B": {
                "Properties": (
                    GATTCharacteristicProperties.read
                    | GATTCharacteristicProperties.write
                    | GATTCharacteristicProperties.indicate
                ),
                "Permissions": (
                    GATTAttributePermissions.readable
                    | GATTAttributePermissions.writeable
                ),
                "Value": None,
            }
        },
        "5c339364-c7be-4f23-b666-a8ff73a6a86a": {
            "bfc0c92f-317d-4ba9-976b-cc11ce77b4ca": {
                "Properties": GATTCharacteristicProperties.read,
                "Permissions": GATTAttributePermissions.readable,
                "Value": bytearray(b"\x69"),
            }
        },
    }
    my_service_name = "Pi Service"
    server = BlessServer(name=my_service_name, loop=loop)
    server.read_request_func = read_request
    server.write_request_func = write_request

    await server.add_gatt(gatt)
    await server.start()
    logger.debug(server.get_characteristic("51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"))
    logger.debug("Advertising")
    logger.info(
        "Write '0xF' to the advertised characteristic: "
        + "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
    )

    # Start listening for commands from master service
    command_listener = asyncio.create_task(listen_for_commands())

    if trigger.__module__ == "threading":
        trigger.wait()
    else:
        await trigger.wait()

    await asyncio.sleep(2)
    logger.debug("Updating")
    server.get_characteristic("51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B").value = bytearray(
        b"i"
    )
    server.update_value(
        "A07498CA-AD5B-474E-940D-16F1FBE7E8CD", "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
    )
    await asyncio.sleep(5)
    await server.stop()

    # Cancel the command listener task
    command_listener.cancel()

    return server

# Initial Bluetooth service
loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
