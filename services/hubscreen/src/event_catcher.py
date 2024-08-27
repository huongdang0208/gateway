import PySimpleGUI as sg

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
                if event == f'-{light_id.upper()}-ON':
                    # Update the GUI and light state
                    self.window[f'-{light_id.upper()}-ON'].update(visible=False)
                    self.window[f'-{light_id.upper()}-OFF'].update(visible=True)
                    self.list_lights[index].state = False  # Update the state in the list
                    self.send_command_to_master(light_id, False, "BLE")
                elif event == f'-{light_id.upper()}-OFF':
                    # Update the GUI and light state
                    self.window[f'-{light_id.upper()}-OFF'].update(visible=False)
                    self.window[f'-{light_id.upper()}-ON'].update(visible=True)
                    self.list_lights[index].state = True  # Update the state in the list
                    self.send_command_to_master(light_id, True, "BLE")
            if event == '-LIGHTS-':
                self.toggle_light_block = True
                self.toggle_switch_block = False
                self.toggle_timer_block = False
                self.update_block('-TOGGLE_LIGHT_BLOCK-')
            elif event == '-SWITCHES-':
                self.toggle_light_block = False
                self.toggle_switch_block = True
                self.toggle_timer_block = False
                self.update_block('-TOGGLE_SWITCH_BLOCK-')
            elif event == '-TIMER-':
                self.toggle_light_block = False
                self.toggle_switch_block = False
                self.toggle_timer_block = True
                self.update_block('-TOGGLE_TIMER_BLOCK-')
            elif event == '-SW1-TOGGLE-GRAPHIC-':   # if the graphical button that changes images
                    self.sw1_graphic_off = not self.sw1_graphic_off
                    self.window['-SW1-TOGGLE-GRAPHIC-'].update(image_data=self.toggle_btn_off if self.sw1_graphic_off else self.toggle_btn_on)
                    self.send_command_to_master('switch-0', not self.sw1_graphic_off, 'MQTT')
            elif event == '-SW2-TOGGLE-GRAPHIC-':   # if the graphical button that changes images
                    self.sw2_graphic_off = not self.sw2_graphic_off
                    self.window['-SW2-TOGGLE-GRAPHIC-'].update(image_data=self.toggle_btn_off if self.sw2_graphic_off else self.toggle_btn_on)
                    self.send_command_to_master('switch-1', not self.sw2_graphic_off, 'MQTT')
            elif event == '-SW3-TOGGLE-GRAPHIC-':   # if the graphical button that changes images
                    self.sw3_graphic_off = not self.sw3_graphic_off
                    self.window['-SW3-TOGGLE-GRAPHIC-'].update(image_data=self.toggle_btn_off if self.sw3_graphic_off else self.toggle_btn_on)
                    self.send_command_to_master('switch-2', not self.sw3_graphic_off, 'MQTT')
            if self.pysimplegui_user_settings.get('-enable debugger-', False):
                print("Debugger is enabled")
        self.window.close()