import os
import sys
import time
import threading
import socket
import paho.mqtt.publish as publish
import paho.mqtt.client as paho
from dotenv import load_dotenv
sys.path.append('../')  # This adds the parent directory to the path
from protobuf import hubscreen_pb2

load_dotenv()

MASTER_SERVICE_SOCKET = "/tmp/gui_service_socket"

class MQTTService:
    def __init__(self):
        self.msgs = [
            {'topic': "hub/lights", 'payload': "01"},
            {'topic': "hub/switches", 'payload': ""},
            {'topic': "adult/news", 'payload': "extra extra"},
            {'topic': "adult/news", 'payload': "super extra"}
        ]

        self.host = "51.79.251.117"
        self.port = 8885

        # Set up MQTT broker credentials from .env file
        self.username = os.getenv('MQTT_SERVER_USERNAME')
        self.password = os.getenv('MQTT_SERVER_PWD')

        # Create a socket for communication with the master service
        self.client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

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
        client.publish('pong', 'ack', 0)

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

        # Keep the client loop running
        while client.loop() == 0:
            pass

    def receive_command_from_master(self):
        try:
            # Connect to the master service Unix Domain Socket
            self.client_socket.connect(MASTER_SERVICE_SOCKET)
            print('Connect successfully')
            while True:
                # Receive command from the master service
                command_data = self.client_socket.recv(1024)

                if not command_data:
                    break

                # Parse the command using Protocol Buffers
                command = hubscreen_pb2.Command()
                command.ParseFromString(command_data)

                # Debug: Print received command details
                print(f"Received command from master: Service={command.service}, Action={command.action}")

                # Publish the message based on the command
                if command.service == "MQTT" and command.action == "Publish":
                    self.publish_single_message(command.payload, "Hello from MQTT Service!")
                elif command.service == "MQTT" and command.action == "Custom":
                    self.publish_single_message(command.payload, "Custom message from MQTT Service!")

        except Exception as e:
            print(f"Error communicating with Master Service: {e}")
        finally:
            # Close the client socket when done
            self.client_socket.close()

    def run(self):
        """Run the MQTT Service."""
        print('Start thread command')
        # Start a separate thread to listen for commands from the master
        command_thread = threading.Thread(target=self.receive_command_from_master)
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
