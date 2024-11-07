import os
import re
import time
import threading
import socket
import paho.mqtt.publish as publish
import paho.mqtt.client as paho
from dotenv import load_dotenv
import hubscreen_pb2

load_dotenv()

MQTT_LISTEN_SERVICE_SOCKET = "/tmp/mqtt_listen_socket"
MQTT_SEND_SERVICE_SOCKET = "/tmp/mqtt_send_socket"

class MQTTService:
    def __init__(self):
        self.msgs = [
            {'topic': "hub/lights", 'payload': "01"},
            {'topic': "hub/switches", 'payload': ""},
            {'topic': "hub/devices", 'payload': ""},
            {'topic': "adult/news", 'payload': "super extra"}
        ]

        self.host = "51.79.251.117"
        self.port = 1883

        # Set up MQTT broker credentials from .env file
        self.username = os.getenv('MQTT_SERVER_USERNAME')
        self.password = os.getenv('MQTT_SERVER_PWD')

    def publish_single_message(self, topic, message):
        print(f"Publishing to topic: {topic}, message: {message}")
        publish.single(
            topic=topic,
            payload=message,
            hostname=self.host,
            port=self.port,
            auth={'username': self.username, 'password': self.password}
        )

    def publish_multiple_messages(self, msgs):
        publish.multiple(msgs, hostname=self.host)

    def on_message(self, client, userdata, msg):
        print(f"Received message on topic: {msg.topic} with QoS {msg.qos} and payload {msg.payload.decode()}")
        
        message = msg.payload.decode()
        print(f"Received message: {message}")
        client.publish('pong', 'ack', 0)
        if (msg.topic == "hub/devices"):
            pattern = r"(add|delete) - \[id:\s*(\d+)\s*(?:,\s*protocol:\s*(\w+))?\s*(?:,\s*name:\s*([^\]]+))?\s*\]"
            match = re.search(pattern, message)
            if match:
                action = match.group(1)
                device_id = int(match.group(2))
                protocol = match.group(3) if match.group(3) else None
                device_name = match.group(4) if match.group(4) else None
                if (protocol == "BLE"):
                    led_device = hubscreen_pb2.Led_t()
                    led_device.id = device_id
                    led_device.state = 0
                    led_device.name = device_name
                    self.send_command_to_master(led_device, action, "GUI", "LED")
                elif (protocol == "MQTT"):
                    sw_device = hubscreen_pb2.Switch_t()
                    sw_device.id = device_id
                    sw_device.state = 0
                    sw_device.name = device_name
                    self.send_command_to_master(sw_device, action, "GUI", "SW")
            else:
                raise ValueError("Message format is incorrect")
        else:
            pattern = r"turn (on|off) - \[state:\s*(\d+)\s*id:\s*(\d+)\s*name:\s*\"([^\"]+)\"\s*\]"
            match = re.search(pattern, message)
            if match:
                action = match.group(1)
                state = int(match.group(2))  # Convert state to integer
                device_id = int(match.group(3))
                device_name = match.group(4)
                if (msg.topic == "hub/lights"):
                    led_device = hubscreen_pb2.Led_t()
                    led_device.id = device_id
                    led_device.state = state
                    led_device.name = device_name
                    self.send_command_to_master(led_device, action, "GUI", "LED")
                else:
                    sw_device = hubscreen_pb2.Switch_t()
                    sw_device.id = device_id
                    sw_device.state = state
                    sw_device.name = device_name
                    self.send_command_to_master(sw_device, action, "GUI", "SW")
            else:
                raise ValueError("Message format is incorrect")

    def on_subscribe(self):
        client = paho.Client()
        client.on_message = self.on_message

        # Set MQTT broker username and password
        client.username_pw_set(username=self.username, password=self.password)

        # Connect to the MQTT broker
        client.connect(self.host, self.port, 60)

        # Subscribe to topics
        client.subscribe("hub/lights", 0)
        client.subscribe("hub/switches", 0)
        client.subscribe("hub/devices", 0)

        # Keep the client loop running
        while client.loop() == 0:
            pass
    
    def handle_command(self, command):
        if command.receiver == "MQTT":
            command_string = f"{command.action} - {command.sw_device}"
            self.publish_single_message("hub/switches", command_string)
        else:
            command_string = f"{command.action} - {command.led_device}"
            self.publish_single_message("hub/lights", command_string)

    def listen_for_commands(self):
        # Ensure the socket path is cleared before binding
        if os.path.exists(MQTT_LISTEN_SERVICE_SOCKET):
            os.remove(MQTT_LISTEN_SERVICE_SOCKET)

        # Create a Unix Domain Socket
        server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_sock.bind(MQTT_LISTEN_SERVICE_SOCKET)
        server_sock.listen(5)

        print("Listening for commands from master service...")

        while True:
            client_sock, _ = server_sock.accept()
            data = client_sock.recv(1024)
            if data:
                # Parse the received data as a Command message using Protobuf
                command = hubscreen_pb2.Command()
                command.ParseFromString(data)
                self.handle_command(command)
                print(f"Received command: {command}")

            client_sock.close()
            
    def send_command_to_master(self, device, action, receiver, type_device):
        command = hubscreen_pb2.Command()
        print(f"Sending command to master: {action}, {receiver}, {type_device}")
        command.action = action
        command.receiver = receiver
        if (type_device == "SW"):
            command.sender = "MQTT"
            command.sw_device.append(device)
        else:
            command.sender = "BLE"
            command.led_device.append(device)

        # Send the command to the master service using a Unix Domain Socket
        client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try: 
            client_sock.connect(MQTT_SEND_SERVICE_SOCKET)
            client_sock.sendall(command.SerializeToString())
            print(f"Sent command to master: {command}")
        except Exception as e:
            print(f"Error sending command to master: {e}")
        finally:
            client_sock.close()

    def run(self):
        """Run the MQTT Service."""
        print('Start thread command')
        # Start a separate thread to listen for commands from the master
        command_thread = threading.Thread(target=self.listen_for_commands)
        command_thread.start()

        # Main loop for processing MQTT-related tasks
        while True:
            try:
                # Process MQTT-related tasks (e.g., handling subscriptions)
                self.on_subscribe()
            except Exception as e:
                print(f"MQTT Service Error: {e}")
            time.sleep(1)

# Initialize and start MQTT service thread
mqtt_service = MQTTService()
mqtt_thread = threading.Thread(target=mqtt_service.run)
mqtt_thread.start()