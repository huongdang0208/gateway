import asyncio
import aioble
import bluetooth
import struct
from machine import Pin
from random import randint

# Init LED
led = Pin(2, Pin.OUT)
led.value(0)

# Init random value
value = 0

# Define UUIDs for the service and characteristics
_BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
_BLE_SENSOR_CHAR_UUID = bluetooth.UUID('19b10001-e8f2-537e-4f6c-d104768a1214')
_BLE_LED_UUID = bluetooth.UUID('19b10002-e8f2-537e-4f6c-d104768a1214')

# Define the advertising interval
_ADV_INTERVAL_MS = 250_000

# Register the GATT server, service, and characteristics
ble_service = aioble.Service(_BLE_SERVICE_UUID)
sensor_characteristic = aioble.Characteristic(ble_service, _BLE_SENSOR_CHAR_UUID, read=True, notify=True)
led_characteristic = aioble.Characteristic(ble_service, _BLE_LED_UUID, read=True, write=True, notify=True, capture=True)

# Register the service
aioble.register_services(ble_service)

# Helper function to encode data as UTF-8
def _encode_data(data):
    return str(data).encode('utf-8')

# Helper function to decode the LED characteristic encoding (bytes)
def _decode_data(data):
    try:
        if data is not None:
            # Decode the UTF-8 data
            number = int.from_bytes(data, 'big')
            return number
    except Exception as e:
        print("Error decoding temperature:", e)
        return None

# Get sensor readings
def get_random_value():
    return randint(0,100)

# Get new value and update characteristic
async def sensor_task():
    while True:
        value = get_random_value()
        sensor_characteristic.write(_encode_data(value), send_update=True)
        print('New random value written: ', value)
        await asyncio.sleep_ms(1000)

# Serially wait for connections. Don't advertise while a central is connected.
async def peripheral_task():
    while True:
        try:
            async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name="Raspi",
                services=[_BLE_SERVICE_UUID],
            ) as connection:
                print("Connection from", connection.device)
                await connection.disconnected()
        except asyncio.CancelledError:
            # Catch the CancelledError
            print("Peripheral task cancelled")
        except Exception as e:
            print("Error in peripheral_task:", e)

# Run the tasks
asyncio.gather(sensor_task(), peripheral_task())