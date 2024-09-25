#include <iostream>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <thread>
#include "hubscreen.pb.h" // Include the generated Protobuf classes

#define GUI_SOCKET_PATH "/tmp/gui_socket"
#define BLE_SOCKET_PATH "/tmp/ble_socket"
#define MQTT_SOCKET_PATH "/tmp/mqtt_socket"
#define AI_SOCKET_PATH "/tmp/ai_socket"

class MasterService
{
private:
    // This function to send command to corresponding service
    void send_to_service(const std::string &service_socket_path, const hubscreen::Command &command)
    {
        int service_sock = socket(AF_UNIX, SOCK_STREAM, 0);
        if (service_sock == -1)
        {
            std::cerr << "Failed to create socket for service: " << service_socket_path << std::endl;
            return;
        };

        struct sockaddr_un service_addr;
        service_addr.sun_family = AF_UNIX;
        strncpy(service_addr.sun_path, service_socket_path.c_str(), sizeof(service_addr.sun_path) - 1);

        if (connect(service_sock, (struct sockaddr *)&service_addr, sizeof(service_addr)) == -1)
        {
            std::cerr << "Failed to connect to service: " << service_socket_path << std::endl;
            close(service_sock);
            return;
        }

        // Serialize the command to a string
        std::string serialized_command;
        command.SerializeToString(&serialized_command);

        // Send the serialized command
        if (send(service_sock, serialized_command.c_str(), serialized_command.size(), 0) == -1)
        {
            std::cerr << "Failed to send data to service: " << service_socket_path << std::endl;
        }

        std::cout << "Sending successfully" << std::endl;

        close(service_sock);
    }

    // Thí function to handle command from service
    void handle_command(const hubscreen::Command &command)
    {
        if (command.receiver() == "BLE")
        {
            std::cout << "Turn into BLE" << std::endl;
            send_to_service(BLE_SOCKET_PATH, command);
        }
        else if (command.receiver() == "MQTT")
        {
            std::cout << "Turn into MQTT" << std::endl;
            send_to_service(MQTT_SOCKET_PATH, command);
        }
        else if (command.receiver() == "AI")
        {
            std::cout << "Turn into AI" << std::endl;
        }
        else
        {
            std::cerr << "Unknown service: " << command.receiver() << std::endl;
        }
    }
    void listen_to_gui()
    {
        int server_sock = socket(AF_UNIX, SOCK_STREAM, 0);
        if (server_sock == -1)
        {
            std::cerr << "Failed to create server socket" << std::endl;
            return;
        }

        struct sockaddr_un server_addr;
        server_addr.sun_family = AF_UNIX;
        strncpy(server_addr.sun_path, GUI_SOCKET_PATH, sizeof(server_addr.sun_path) - 1);
        unlink(GUI_SOCKET_PATH); // Ensure the socket doesn't already exist

        if (bind(server_sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1)
        {
            std::cerr << "Failed to bind server socket" << std::endl;
            close(server_sock);
            return;
        }

        if (listen(server_sock, 5) == -1)
        {
            std::cerr << "Failed to listen on server socket" << std::endl;
            close(server_sock);
            return;
        }

        std::cout << "Listening for GUI commands..." << std::endl;

        while (true)
        {
            int client_sock = accept(server_sock, NULL, NULL);
            if (client_sock == -1)
            {
                std::cerr << "Failed to accept connection" << std::endl;
                continue;
            }

            char buffer[1024];
            ssize_t bytes_received = recv(client_sock, buffer, sizeof(buffer), 0);
            if (bytes_received > 0)
            {
                hubscreen::Command command;
                std::cout << "Bytes received: " << bytes_received << std::endl;
                std::string command_str(buffer, bytes_received);
                std::cout << "Command string: " << command_str << std::endl;
                if (command.ParseFromArray(buffer, bytes_received))
                {
                    std::cout << "Received command: " << command.DebugString() << std::endl;
                    handle_command(command);
                }
                else
                {
                    std::cerr << "Failed to parse command" << command.ParseFromArray(buffer, bytes_received) << std::endl;
                }
            }
            else
            {
                std::cerr << "Failed to receive data" << std::endl;
            }

            close(client_sock);
        }

        close(server_sock);
    }

    void listen_to_service(const std::string &service_socket_path, const std::string &service_name)
    {
        int server_sock = socket(AF_UNIX, SOCK_STREAM, 0);
        if (server_sock == -1)
        {
            std::cerr << "Failed to create socket for service: " << service_name << std::endl;
            return;
        }

        struct sockaddr_un server_addr;
        server_addr.sun_family = AF_UNIX;
        strncpy(server_addr.sun_path, service_socket_path.c_str(), sizeof(server_addr.sun_path) - 1);
        unlink(service_socket_path.c_str()); // Ensure the socket doesn't already exist

        if (bind(server_sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1)
        {
            std::cerr << "Failed to bind socket for service: " << service_name << std::endl;
            close(server_sock);
            return;
        }

        if (listen(server_sock, 5) == -1)
        {
            std::cerr << "Failed to listen on socket for service: " << service_name << std::endl;
            close(server_sock);
            return;
        }

        std::cout << "Listening for messages from " << service_name << " service..." << std::endl;

        while (true)
        {
            int client_sock = accept(server_sock, NULL, NULL);
            if (client_sock == -1)
            {
                std::cerr << "Failed to accept connection from " << service_name << std::endl;
                continue;
            }

            char buffer[1024];
            ssize_t bytes_received = recv(client_sock, buffer, sizeof(buffer), 0);
            if (bytes_received > 0)
            {
                hubscreen::Command command;
                if (command.ParseFromArray(buffer, bytes_received))
                {
                    std::cout << "Received response from " << service_name << ": " << command.DebugString() << std::endl;
                    // Handle response from BLE or MQTT services
                }
                else
                {
                    std::cerr << "Failed to parse response from " << service_name << std::endl;
                }
            }
            else
            {
                std::cerr << "Failed to receive data from " << service_name << std::endl;
            }

            close(client_sock);
        }

        close(server_sock);
    }

public:
    MasterService()
    {
        GOOGLE_PROTOBUF_VERIFY_VERSION;
    }

    ~MasterService()
    {
        google::protobuf::ShutdownProtobufLibrary();
    }

    void start()
    {
        std::thread gui_listener(&MasterService::listen_to_gui, this);
        std::thread ai_listener(&MasterService::listen_to_service, this, AI_SOCKET_PATH, "AI");
        std::thread ble_listener(&MasterService::listen_to_service, this, BLE_SOCKET_PATH, "BLE");
        std::thread mqtt_listener(&MasterService::listen_to_service, this, MQTT_SOCKET_PATH, "MQTT");

        gui_listener.join();
        ai_listener.join();
        ble_listener.join();
        mqtt_listener.join();
    }
};

int main()
{
    MasterService master_service;
    master_service.start();

    return 0;
}