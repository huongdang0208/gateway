#include <iostream>
#include <thread>
#include <queue>
#include <string>
#include <mutex>
#include <condition_variable>
#include <cstring>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <hubscreen.pb.h>

const int MQTT_SERVICE_PORT = 5001;
const int BLE_SERVICE_PORT = 5002;
const int GUI_SERVICE_PORT = 5003;

std::mutex queue_mutex;
std::condition_variable queue_cv;
std::queue<hubscreen::Command> command_queue;

class MasterService {
public:
    void start() {
        std::thread mqtt_thread(&MasterService::listen, this, MQTT_SERVICE_PORT);
        std::thread ble_thread(&MasterService::listen, this, BLE_SERVICE_PORT);
        std::thread gui_thread(&MasterService::listen, this, GUI_SERVICE_PORT);

        mqtt_thread.detach();
        ble_thread.detach();
        gui_thread.detach();

        std::cout << "Master Service started." << std::endl;

        while (true) {
            processCommands();
        }
    }

private:
    void listen(int port) {
        int server_socket;
        struct sockaddr_in address;
        int opt = 1;

        if ((server_socket = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
            std::cerr << "Socket failed" << std::endl;
            exit(EXIT_FAILURE);
        }

        if (setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
            std::cerr << "Setsockopt failed" << std::endl;
            exit(EXIT_FAILURE);
        }

        address.sin_family = AF_INET;
        address.sin_addr.s_addr = INADDR_ANY;
        address.sin_port = htons(port);

        if (bind(server_socket, (struct sockaddr*)&address, sizeof(address)) < 0) {
            std::cerr << "Bind failed" << std::endl;
            exit(EXIT_FAILURE);
        }

        if (listen(server_socket, 3) < 0) {
            std::cerr << "Listen failed" << std::endl;
            exit(EXIT_FAILURE);
        }

        std::cout << "Listening on port " << port << std::endl;

        while (true) {
            int client_socket;
            struct sockaddr_in client_address;
            socklen_t client_len = sizeof(client_address);

            if ((client_socket = accept(server_socket, (struct sockaddr*)&client_address, &client_len)) < 0) {
                std::cerr << "Accept failed" << std::endl;
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

        control_messages::Command command;
        command.ParseFromArray(buffer, valread);

        std::unique_lock<std::mutex> lock(queue_mutex);
        command_queue.push(command);
        queue_cv.notify_one();

        control_messages::Response response = processCommand(command);

        std::string response_str;
        response.SerializeToString(&response_str);

        send(client_socket, response_str.c_str(), response_str.size(), 0);
        close(client_socket);
    }

    control_messages::Response processCommand(const control_messages::Command& command) {
        control_messages::Response response;
        response.set_status("Success");
        response.set_message("Command processed successfully");

        std::cout << "Processing command for " << command.service() << std::endl;

        if (command.service() == "MQTT") {
            return sendToService(MQTT_SERVICE_PORT, command);
        } else if (command.service() == "BLE") {
            return sendToService(BLE_SERVICE_PORT, command);
        } else if (command.service() == "GUI") {
            return sendToService(GUI_SERVICE_PORT, command);
        } else {
            response.set_status("Failed");
            response.set_message("Service not found");
        }

        return response;
    }

    control_messages::Response sendToService(int port, const control_messages::Command& command) {
        control_messages::Response response;
        int sock = 0;
        struct sockaddr_in serv_addr;

        if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
            response.set_status("Failed");
            response.set_message("Socket creation error");
            return response;
        }

        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(port);

        if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
            response.set_status("Failed");
            response.set_message("Invalid address");
            return response;
        }

        if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
            response.set_status("Failed");
            response.set_message("Connection failed");
            return response;
        }

        std::string command_str;
        command.SerializeToString(&command_str);

        send(sock, command_str.c_str(), command_str.size(), 0);

        char buffer[1024] = {0};
        int valread = read(sock, buffer, 1024);

        if (valread > 0) {
            response.ParseFromArray(buffer, valread);
        } else {
            response.set_status("Failed");
            response.set_message("No response from service");
        }

        close(sock);
        return response;
    }

    void processCommands() {
        std::unique_lock<std::mutex> lock(queue_mutex);

        while (command_queue.empty()) {
            queue_cv.wait(lock);
        }

        while (!command_queue.empty()) {
            control_messages::Command command = command_queue.front();
            command_queue.pop();

            control_messages::Response response = processCommand(command);

            std::cout << "Processed command: " << response.message() << std::endl;
        }
    }
};

int main() {
    GOOGLE_PROTOBUF_VERIFY_VERSION;

    MasterService master_service;
    master_service.start();

    google::protobuf::ShutdownProtobufLibrary();

    return 0;
}
