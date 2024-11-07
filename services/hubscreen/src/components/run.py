import os
import socket
import threading
import PySimpleGUI as sg
import services.hubscreen.src.components.hubscreen_pb2 as hubscreen_pb2

GUI_LISTEN_SERVICE_SOCKET = "/tmp/gui_listen_socket"

def run(self):
        # self.update_ip_address()
        while True:  # Event Loop
            event, values = self.window.read()
            # temp, humidity = read_sht30_data()
            # window['-TEMP-'].update(temp)
            # window['-HUMID-'].update(humidity)
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            # Iterate over each light to handle events dynamically
            for index, light in enumerate(self.list_lights):
                light_id = light.id
                if event == f'-{str(light_id).upper()}-ON':
                    # Update the GUI and light state
                    self.window[f'-{str(light_id).upper()}-ON'].update(visible=False)
                    self.window[f'-{str(light_id).upper()}-OFF'].update(visible=True)
                    self.list_lights[index].state = False  # Update the state in the list
                    self.send_command_to_master(light_id, False, "BLE")
                elif event == f'-{str(light_id).upper()}-OFF':
                    # Update the GUI and light state
                    self.window[f'-{str(light_id).upper()}-OFF'].update(visible=False)
                    self.window[f'-{str(light_id).upper()}-ON'].update(visible=True)
                    self.list_lights[index].state = True  # Update the state in the list
                    self.send_command_to_master(light_id, True, "BLE")
                    
            for index, switch in enumerate(self.list_switches):
                switch_id = switch.id
                if event == f'-{str(switch_id).upper()}-TOGGLE-GRAPHIC-':
                    # Update the GUI and light state
                    self.list_switches[index].state = not self.list_switches[index].state  # Update the state in the list
                    self.window[f'-{str(switch_id).upper()}-TOGGLE-GRAPHIC-'].update(image_data= self.toggle_btn_on if  self.list_switches[index].state else self.toggle_btn_off )
                    self.send_command_to_master(self.list_switches[index].id, self.list_switches[index].state, 'MQTT')
            if event == '-LIGHTS-':
                self.toggle_light_block = True
                self.toggle_switch_block = False
                self.toggle_timer_block = False
                self.toggle_ai_block = False
                self.update_block('-TOGGLE_LIGHT_BLOCK-')
            elif event == '-SWITCHES-':
                self.toggle_light_block = False
                self.toggle_switch_block = True
                self.toggle_timer_block = False
                self.toggle_ai_block = False
                self.update_block('-TOGGLE_SWITCH_BLOCK-')
            elif event == '-TIMER-':
                self.toggle_light_block = False
                self.toggle_switch_block = False
                self.toggle_timer_block = True
                self.toggle_ai_block = False
                self.update_block('-TOGGLE_TIMER_BLOCK-')
            elif event == '-ASSISTANT-':
                self.toggle_light_block = False
                self.toggle_switch_block = False
                self.toggle_timer_block = False
                self.toggle_ai_block = True
                self.update_block('-TOGGLE_AI_BLOCK-')
            elif event == '-ASSISTANT-START-':
                self.ai_thread = threading.Thread(target=self.assistant.listen_for_wake_word)
                self.ai_thread.start()
                self.window['-WAKE-WORD-START-'].update(visible=True)
            elif event == '-ASSISTANT-STOP-':
                self.assistant.cleanup()
                self.ai_thread.join()  # Wait for the thread to finish
                # self.window['-WAKE-WORD-START-'].update(visible=False)

            if self.pysimplegui_user_settings.get('-enable debugger-', False):
                print("Debugger is enabled")
        self.window.close()
        
def listen_for_commands(self):
    if os.path.exists(GUI_LISTEN_SERVICE_SOCKET):
        os.remove(GUI_LISTEN_SERVICE_SOCKET)
    # Create a Unix Domain Socket
    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_socket.bind(GUI_LISTEN_SERVICE_SOCKET)
    server_socket.listen(1)
    print("Listening for commands from master service...")
    while True:
        client_socket,_ = server_socket.accept()
        data = client_socket.recv(1024)
        if data:
            command = hubscreen_pb2.Command()
            command.ParseFromString(data)
            print(f"Received command: {command}")
            if (command.action == 'add' or command.action == 'delete'):
                if command.sender == "BLE":
                    for light in command.led_device:
                        if command.action == 'add':
                            self.list_lights.append(light)
                            self.create_new_device_content_block(light, "BLE")
                        else:
                            self.list_lights.remove(light)
                            self.remove_device_content_block(light, "BLE")
                else:
                    for sw in command.sw_device:
                        if command.action == 'add':
                            self.list_switches.append(sw)
                            self.create_new_device_content_block(sw, "MQTT")
                        else:
                            self.list_switches.remove(sw)
                            self.remove_device_content_block(sw, "MQTT")
            else:
                if command.sender == 'BLE':
                    for light in command.led_device:
                        light_id = light.id
                        if command.action == "turn on":
                            self.window[f'-{str(light_id).upper()}-OFF'].update(visible=False)
                            self.window[f'-{str(light_id).upper()}-ON'].update(visible=True)
                        else:
                            self.window[f'-{str(light_id).upper()}-ON'].update(visible=False)
                            self.window[f'-{str(light_id).upper()}-OFF'].update(visible=True)
                else:
                    for sw in command.sw_device:
                        sw_id = sw.id
                        if command.action == "turn on":
                            self.window[f'-{str(sw_id).upper()}-TOGGLE-GRAPHIC-'].update(image_data= self.toggle_btn_on)
                        else:
                            self.window[f'-{str(sw_id).upper()}-TOGGLE-GRAPHIC-'].update(image_data= self.toggle_btn_off)
        client_socket.close()