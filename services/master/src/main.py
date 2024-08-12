import socket
import threading
import sys
sys.path.append('../')  # This adds the parent directory to the path
from protobuf import hubscreen_pb2

# Paths for Unix domain sockets
GUI_SOCKET_PATH = "/tmp/gui_socket_service"
BLE_SOCKET_PATH = "/tmp/ble_socket_service"
MQTT_SOCKET_PATH = "/tmp/mqtt_socket_service"

def handle_command(command):
    if command.service == "BLE":
        send_to_service(BLE_SOCKET_PATH, command)
    elif command.service == "MQTT":
        send_to_service(MQTT_SOCKET_PATH, command)
    else:
        print("Unknown service:", command.service)

def send_to_service(service_socket_path, command):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as service_sock:
        try:
            service_sock.connect(service_socket_path)
            service_sock.sendall(command.SerializeToString())
        except Exception as e:
            print(f"Failed to send to service {service_socket_path}: {e}")

def listen_to_gui():
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server_sock:
        server_sock.bind(GUI_SOCKET_PATH)
        server_sock.listen(1)
        print("Listening for GUI commands...")

        while True:
            conn, _ = server_sock.accept()
            with conn:
                data = conn.recv(1024)
                if not data:
                    continue
                command = hubscreen_pb2.Command()
                command.ParseFromString(data)
                print(f"Received command: {command}")
                handle_command(command)

def main():
    gui_listener_thread = threading.Thread(target=listen_to_gui)
    gui_listener_thread.start()

    # Other initialization tasks for the master service can go here

    gui_listener_thread.join()

if __name__ == "__main__":
    main()
