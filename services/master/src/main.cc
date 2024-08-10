#include <iostream>
#include <thread>
#include <queue>
#include <string>
#include <mutex>
#include <condition_variable>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <hubscreen.pb.h>

const std::string MQTT_SERVICE_SOCKET = "/tmp/mqtt_service_socket";
const std::string BLE_SERVICE_SOCKET = "/tmp/ble_service_socket";
const std::string GUI_SERVICE_SOCKET = "/tmp/gui_service_socket";

std::mutex queue_mutex;
std::condition_variable queue_cv;
std::queue<hubscreen::Command> command_queue;

class MasterService {
public:
    void start() {
        // Create a thread for each service to listen on Unix Domain Sockets
        std::thread mqtt_thread(&MasterService::listen_service, this, MQTT_SERVICE_SOCKET);
        std::thread ble_thread(&MasterService::listen_service, this, BLE_SERVICE_SOCKET);
        std::thread gui_thread(&MasterService::listen_service, this, GUI_SERVICE_SOCKET);

        mqtt_thread.detach();
        ble_thread.detach();
        gui_thread.detach();

        std::cout << "Master Service started." << std::endl;

        while (true) {
            processCommands();
        }
    }

private:
    void listen_service(const std::string& socket_path) {
        int server_socket;
        struct sockaddr_un address;

        // Create Unix Domain Socket
        if ((server_socket = socket(AF_UNIX, SOCK_STREAM, 0)) == 0) {
            std::cerr << "Socket creation failed" << std::endl;
            exit(EXIT_FAILURE);
        }

        // Remove any existing file at the socket path
        unlink(socket_path.c_str());

        // Set up the address structure for Unix Domain Socket
        memset(&address, 0, sizeof(address));
        address.sun_family = AF_UNIX;
        strncpy(address.sun_path, socket_path.c_str(), sizeof(address.sun_path) - 1);

        // Bind the socket to the path
        if (bind(server_socket, (struct sockaddr*)&address, sizeof(address)) < 0) {
            std::cerr << "Bind failed on path: " << socket_path << std::endl;
            exit(EXIT_FAILURE);
        }

        // Start listening for connections
        if (listen(server_socket, 3) < 0) {
            std::cerr << "Listen failed on path: " << socket_path << std::endl;
            exit(EXIT_FAILURE);
        }

        std::cout << "Listening on socket path: " << socket_path << std::endl;

        while (true) {
            int client_socket;
            struct sockaddr_un client_address;
            socklen_t client_len = sizeof(client_address);

            // Accept a connection from a client service
            if ((client_socket = accept(server_socket, (struct sockaddr*)&client_address, &client_len)) < 0) {
                std::cerr << "Accept failed on path: " << socket_path << std::endl;
                continue;
            }

            std::thread(&MasterService::handleConnection, this, client_socket).detach();
        }
    }

    void handleConnection(int client_socket) {
        char buffer[1024] = {0};
        int valread = read(client_socket, buffer, 1024);

        if (valread <= 0) {
            close(client_socket);
            return;
        }

        hubscreen::Command command;
        command.ParseFromArray(buffer, valread);

        // Lock the mutex to ensure thread-safe access to the command queue
        std::unique_lock<std::mutex> lock(queue_mutex);
        command_queue.push(command);
        queue_cv.notify_one(); // Notify the processing thread

        // Process the command and send a response back
        hubscreen::Response response = processCommand(command);

        std::string response_str;
        response.SerializeToString(&response_str);

        send(client_socket, response_str.c_str(), response_str.size(), 0);
        close(client_socket); // Close the client connection
    }

    hubscreen::Response processCommand(const hubscreen::Command& command) {
        hubscreen::Response response;
        response.set_status("Success");
        response.set_message("Command processed successfully");

        std::cout << "Processing command for " << command.service() << std::endl;

        // Route the command to the appropriate service based on its name
        if (command.service() == "MQTT") {
            return sendToService(MQTT_SERVICE_SOCKET, command);
        } else if (command.service() == "BLE") {
            return sendToService(BLE_SERVICE_SOCKET, command);
        } else if (command.service() == "GUI") {
            return sendToService(GUI_SERVICE_SOCKET, command);
        } else {
            response.set_status("Failed");
            response.set_message("Service not found");
        }

        return response;
    }

    hubscreen::Response sendToService(const std::string& socket_path, const hubscreen::Command& command) {
        hubscreen::Response response;
        int sock;
        struct sockaddr_un serv_addr;

        if ((sock = socket(AF_UNIX, SOCK_STREAM, 0)) < 0) {
            response.set_status("Failed");
            response.set_message("Socket creation error");
            return response;
        }

        // Set up the server address structure for Unix Domain Socket
        memset(&serv_addr, 0, sizeof(serv_addr));
        serv_addr.sun_family = AF_UNIX;
        strncpy(serv_addr.sun_path, socket_path.c_str(), sizeof(serv_addr.sun_path) - 1);

        // Connect to the service's Unix Domain Socket
        if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
            response.set_status("Failed");
            response.set_message("Connection failed to service at " + socket_path);
            return response;
        }

        std::string command_str;
        command.SerializeToString(&command_str);

        // Send the command to the service
        send(sock, command_str.c_str(), command_str.size(), 0);
        std::cout << "Sending message successfully " << command.action() << std::endl;

        char buffer[1024] = {0};
        int valread = read(sock, buffer, 1024);

        if (valread > 0) {
            response.ParseFromArray(buffer, valread);
        } else {
            response.set_status("Failed");
            response.set_message("No response from service");
        }

        close(sock); // Close the connection to the service
        return response;
    }

    void processCommands() {
        std::unique_lock<std::mutex> lock(queue_mutex);

        // Wait for new commands to be available in the queue
        while (command_queue.empty()) {
            queue_cv.wait(lock);
        }

        while (!command_queue.empty()) {
            hubscreen::Command command = command_queue.front();
            command_queue.pop();

            // Process each command and output the response
            std::cout << "Service of command: " << command.service() << std::endl;
            std::cout << "Action of command: " << command.action() << std::endl;
            hubscreen::Response response = processCommand(command);
            std::cout << "Processed command: " << response.message() << std::endl;
        }
    }
};

int main() {
    // Verify Protocol Buffers version
    GOOGLE_PROTOBUF_VERIFY_VERSION;

    MasterService master_service;
    master_service.start();

    // Shutdown Protocol Buffers library
    google::protobuf::ShutdownProtobufLibrary();

    return 0;
}
