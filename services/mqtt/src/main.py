import os
import sys
import time
import threading
import socket
import paho.mqtt.publish as publish
import paho.mqtt.client as paho
from dotenv import load_dotenv
import hubscreen_pb2

load_dotenv()

MQTT_SERVICE_SOCKET = "/tmp/mqtt_socket"

class MQTTService:
    def __init__(self):
        self.msgs = [
            {'topic': "hub/lights", 'payload': "01"},
            {'topic': "hub/switches", 'payload': ""},
            {'topic': "adult/news", 'payload': "extra extra"},
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
    
    def handle_command(self, command):
        if command.receiver == "MQTT":
            command_string = f"{command.action} - {command.sw_device}"
            self.publish_single_message("hub/switches", command_string)
        else:
            command_string = f"{command.action} - {command.led_device}"
            self.publish_single_message("hub/lights", command_string)


    def listen_for_commands(self):
        # Ensure the socket path is cleared before binding
        if os.path.exists(MQTT_SERVICE_SOCKET):
            os.remove(MQTT_SERVICE_SOCKET)

        # Create a Unix Domain Socket
        server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_sock.bind(MQTT_SERVICE_SOCKET)
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
