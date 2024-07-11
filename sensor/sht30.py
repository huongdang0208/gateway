import smbus
import time

def read_sht30_data():
    # Create I2C bus
    bus = smbus.SMBus(1)  # Use bus 1 (check your Raspberry Pi configuration)

    # SHT30 I2C address
    address = 0x44

    while True:
        try:
            # Send measurement command (0x2C) for high repeatability measurement (0x06)
            bus.write_i2c_block_data(address, 0x2C, [0x06])
            time.sleep(1)

            # Read 6 bytes of data
            data = bus.read_i2c_block_data(address, 0, 6)

            # Convert the data
            temp = (data[0] << 8) + data[1]
            cTemp = -45 + (175 * temp / 65535.0)
            humidity = 100 * ((data[3] << 8) + data[4]) / 65535.0

            # Print the results (you can update LVGL labels here)
            print(f"Temperature: {cTemp:.2f} °C, Humidity: {humidity:.2f} %RH")

            # Sleep for 5 minutes (300 seconds)
            time.sleep(300)

            return cTemp, humidity

        except Exception as e:
            print(f"Error: {e}")

