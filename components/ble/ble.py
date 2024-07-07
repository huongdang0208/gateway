from bluepy.btle import Peripheral, UUID, DefaultDelegate
import time

# Define the UUIDs for the service and characteristics
SERVICE_UUID = UUID("0000180f-0000-1000-8000-00805f9b34fb")
CHARACTERISTIC_UUID = UUID("00002a19-0000-1000-8000-00805f9b34fb")

class MyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print(f"Received data: {data.decode()}")

# Connect to the ESP32 peripheral
peripheral = Peripheral("fc:e8:c0:7c:99:0e", "public")
peripheral.setDelegate(MyDelegate())

# Discover the service and characteristic
service = peripheral.getServiceByUUID(SERVICE_UUID)
characteristic = service.getCharacteristics(CHARACTERISTIC_UUID)[0]

# Enable notifications
peripheral.writeCharacteristic(characteristic.valHandle + 1, b"\x01\x00", withResponse=True)

try:
    while True:
        # Send data to ESP32
        data_to_send = input("Enter data to send: ")
        characteristic.write(data_to_send.encode(), withResponse=True)
        time.sleep(1)
finally:
    peripheral.disconnect()
