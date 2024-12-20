
import os
import requests
import threading
import PySimpleGUI as sg
import pytz
import socket
from datetime import datetime
import services.hubscreen.src.components.hubscreen_pb2 as hubscreen_pb2
from services.hubscreen.src.components.run import run, listen_for_commands
from services.hubscreen.src.components.network import is_connected
from services.hubscreen.src.components.graphql import query_devices_by_license
from  services.hubscreen.src.components.voice_assistant import AIVoiceAssistant

# Constants
GUI_LISTEN_SERVICE_SOCKET = "/tmp/gui_listen_socket"
GUI_SEND_SERVICE_SOCKET = "/tmp/gui_send_socket"
IST = pytz.timezone('Asia/Ho_Chi_Minh')
GRAPHQL_URL = os.getenv("GRAPHQL_ENDPOINT", "https://btabc.dhpgo.com/graphql")
HUB_LICENSE_KEY = os.getenv("HUB_LICENSE_KEY", "123456")

# Define a Singleton class for shared data
class Singleton:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls)
            cls._instance.date_now = ""
            cls._instance.time_now = ""
        return cls._instance

# GUI Interface Class
class InterfaceGraphic:
    def __init__(self):
        self.singleton = Singleton()  # Instance of Singleton
        self.pysimplegui_user_settings = sg.UserSettings()
        self.list_lights = []
        self.list_switches = []
        
        self.assistant = AIVoiceAssistant()
        
        self.light_content_block = []
        self.switch_content_block = []
        
        # Initialize window components
        self.window = self.create_window()
        self.toggle_light_block = True
        self.toggle_switch_block = False
        self.toggle_timer_block = False
        self.toggle_ai_block = False
        
        self.sw1_graphic_off = True
        self.sw2_graphic_off = True
        self.sw3_graphic_off = True
        self.toggle_btn_off = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAED0lEQVRYCe1WTWwbRRR+M/vnv9hO7BjHpElMKSlpqBp6gRNHxAFVcKM3qgohQSqoqhQ45YAILUUVDRxAor2VAweohMSBG5ciodJUSVqa/iikaePEP4nj2Ovdnd1l3qqJksZGXscVPaylt7Oe/d6bb9/svO8BeD8vA14GvAx4GXiiM0DqsXv3xBcJU5IO+RXpLQvs5yzTijBmhurh3cyLorBGBVokQG9qVe0HgwiXLowdy9aKsY3g8PA5xYiQEUrsk93JTtjd1x3siIZBkSWQudUK4nZO1w3QuOWXV+HuP/fL85klAJuMCUX7zPj4MW1zvC0Ej4yMp/w++K2rM9b70sHBYCjo34x9bPelsgp/XJksZ7KFuwZjr3732YcL64ttEDw6cq5bVuCvgy/sje7rT0sI8PtkSHSEIRIKgCQKOAUGM6G4VoGlwiqoVd2Za9Vl8u87bGJqpqBqZOj86eEHGNch+M7otwHJNq4NDexJD+59RiCEQG8qzslFgN8ibpvZNsBifgXmFvJg459tiOYmOElzYvr2bbmkD509e1ylGEZk1Y+Ssfan18n1p7vgqVh9cuiDxJPxKPT3dfGXcN4Tp3dsg/27hUQs0qMGpRMYjLz38dcxS7Dm3nztlUAb38p0d4JnLozPGrbFfBFm79c8hA3H2AxcXSvDz7/+XtZE1kMN23hjV7LTRnKBh9/cZnAj94mOCOD32gi2EUw4FIRUMm6LGhyiik86nO5NBdGRpxYH14bbjYfJteN/OKR7UiFZVg5T27QHYu0RBxoONV9W8KQ7QVp0iXdE8fANUGZa0QAvfhhXlkQcmjJZbt631oIBnwKmacYoEJvwiuFgWncWnXAtuVBBEAoVVXWCaQZzxmYuut68b631KmoVBEHMUUrJjQLXRAQVSxUcmrKVHfjWWjC3XOT1FW5QrWpc5IJdQhDKVzOigEqS5dKHMVplnNOqrmsXqUSkn+YzWaHE9RW1FeXL7SKZXBFUrXW6jIV6YTEvMAUu0W/G3kcxPXP5ylQZs4fa6marcWvvZfJu36kuHjlc/nMSuXz+/ejxgqPFpuQ/xVude9eu39Jxu27OLvBGoMjrUN04zrNMbgVmOBZ96iPdPZmYntH5Ls76KuxL9NyoLA/brav7n382emDfHqeooXyhQmARVhSnAwNNMx5bu3V1+habun5nWdXhwJZ2C5mirTesyUR738sv7g88UQ0rEkTDlp+1wwe8Pf0klegUenYlgyg7bby75jUTITs2rhCAXXQ2vwxz84vlB0tZ0wL4NEcLX/04OrrltG1s8aOrHhk51SaK0us+n/K2xexBxljcsm1n6x/Fuv1PCWGiKOaoQCY1Vb9gWPov50+fdEqd21ge3suAlwEvA14G/ucM/AuppqNllLGPKwAAAABJRU5ErkJggg=='   
        self.toggle_btn_on = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAD+UlEQVRYCe1XzW8bVRCffbvrtbP+2NhOD7GzLm1VoZaPhvwDnKBUKlVyqAQ3/gAkDlWgPeVQEUCtEOIP4AaHSI0CqBWCQyXOdQuRaEFOk3g3IMWO46+tvZ+PeZs6apq4ipON1MNafrvreTPzfvub92bGAOEnZCBkIGQgZOClZoDrh25y5pdjruleEiX+A+rCaQo05bpuvJ/+IHJCSJtwpAHA/e269g8W5RbuzF6o7OVjF8D3Pr4tSSkyjcqfptPDMDKSleW4DKIggIAD5Yf+Oo4DNg6jbUBlvWLUNutAwZu1GnDjzrcXzGcX2AHw/emFUV6Sfk0pqcKpEydkKSo9q3tkz91uF5aWlo1Gs/mYc+i7tz4//19vsW2AU9O381TiioVCQcnlRsWeQhD3bJyH1/MiFLICyBHiuzQsD1arDvypW7DR9nzZmq47q2W95prm+I9fXfqXCX2AF2d+GhI98Y8xVX0lnxvl2UQQg0csb78ag3NjEeD8lXZ7pRTgftmCu4864OGzrq+5ZU0rCa3m+NzXlzvoAoB3+M+SyWQuaHBTEzKMq/3BMbgM+FuFCDBd9kK5XI5PJBKqLSev+POTV29lKB8rT0yMD0WjUSYLZLxzNgZvIHODOHuATP72Vwc6nQ4Uiw8MUeBU4nHS5HA6TYMEl02wPRcZBJuv+ya+UCZOIBaLwfCwQi1Mc4QXhA+PjWRkXyOgC1uIhW5Qd8yG2TK7kSweLcRGKKVnMNExWWBDTQsH9qVmtmzjiThQDs4Qz/OUSGTwcLwIQTLW58i+yOjpXDLqn1tgmDzXzRCk9eDenjo9yhvBmlizrB3V5dDrNTuY0A7opdndStqmaQLPC1WCGfShYRgHdLe32UrV3ntiH9LliuNrsToNlD4kruN8v75eafnSgC6Luo2+B3fGKskilj5muV6pNhk2Qqg5v7lZ51nBZhNBjGrbxfI1+La5t2JCzfD8RF1HTBGJXyDzs1MblONulEqPDVYXgwDIfNx91IUVbAbY837GMur+/k/XZ75UWmJ77ou5mfM1/0x7vP1ls9XQdF2z9uNsPzosXPNFA5m0/EX72TBSiqsWzN8z/GZB08pWq9VeEZ+0bjKb7RTD2i1P4u6r+bwypo5tZUumEcDAmuC3W8ezIqSGfE6g/sTd1W5p5bKjaWubrmWd29Fu9TD0GlYlmTx+8tTJoZeqYe2BZC1/JEU+wQR5TVEUPptJy3Fs+Vkzgf8lemqHumP1AnYoMZSwsVEz6o26i/G9Lgitb+ZmLu/YZtshfn5FZDPBCcJFQRQ+8ih9DctOFvdLIKHH6uUQnq9yhFu0bec7znZ+xpAGmuqef5/wd8hAyEDIQMjAETHwP7nQl2WnYk4yAAAAAElFTkSuQmCC'

        # run(self)
        run_thread = threading.Thread(target=run, args=(self,))
        listen_master_thread = threading.Thread(target=listen_for_commands, args=(self,))
        
        run_thread.start()
        # run_thread.join()
        listen_master_thread.start()
        # listen_master_thread.join()
        
        
    def create_devices_with_no_connection(self):
        light1 = hubscreen_pb2.Led_t(state=0, id=1, name="Light 1", pin=1)
        light2 = hubscreen_pb2.Led_t(state=1, id=2, name="Light 2", pin=2)
        light3 = hubscreen_pb2.Led_t(state=0, id=3, name="Light 3", pin=3)

        # Add these instances to the list
        self.list_lights.append(light1)
        self.list_lights.append(light2)
        self.list_lights.append(light3)
        
        sw1 = hubscreen_pb2.Switch_t(state=0, id=1, name="Switch 1", pin=1)
        sw2 = hubscreen_pb2.Switch_t(state=0, id=2, name="Switch 2", pin=2) 
        sw3 = hubscreen_pb2.Switch_t(state=0, id=3, name="Switch 3", pin=3)
        
        self.list_switches.append(sw1)
        self.list_switches.append(sw2)
        self.list_switches.append(sw3)
        
    def query_devices_by_license(self, query, license):
        try: 
            response = requests.post(GRAPHQL_URL, json={"query": query, "variables": {"license": license}})
            response_data = response.json()
            print(response_data)
            if response.status_code == 200 and 'data' in response_data:
                devices = response_data['data']['devices_by_license']['items']
                for device in devices:
                    if device['protocol'] == 'BLE':
                        light = hubscreen_pb2.Led_t(state=device['current_state'], id=device['id'], name=device['device_name'])
                        self.list_lights.append(light)
                    elif device['protocol'] == 'MQTT':
                        switch = hubscreen_pb2.Switch_t(state=device['current_state'], id=device['id'], name=device['device_name'])
                        self.list_switches.append(switch)
                return devices
            else:
                self.create_devices_with_no_connection()
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            self.create_devices_with_no_connection()
            return None

    def create_window(self):
        # Define themes and colors
        theme_dict = {'BACKGROUND': '#c8d4e4',
                    'TEXT': '#0C0C0C',
                    'INPUT': '#F2EFE8',
                    'TEXT_INPUT': '#0C0C0C',
                    'SCROLL': '#F2EFE8',
                    'BUTTON': ('#0C0C0C', '#C2D4D8'),
                    'PROGRESS': ('#FFFFFF', '#C7D5E0'),
                    'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0}

        # Create instances of Led_t
        if is_connected():
            self.query_devices_by_license(query_devices_by_license, HUB_LICENSE_KEY)
        else:
            self.create_devices_with_no_connection()

        # sg.theme_add_new('Dashboard', theme_dict)     # if using 4.20.0.1+
        sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
        sg.theme('Dashboard')

        BORDER_COLOR = '#C7D5E0'
        WHITE_COLOR = '#FFFFFF'
        DARK_HEADER_COLOR = '#1B2838'
        BLACK_BACKGROUND = '#cfd6b8'
        GRAY_BACKGROUND = '#858585'
        BPAD_TOP = ((10, 10), (10, 5))
        BPAD_LEFT = ((10, 0), (0, 20))
        BPAD_LEFT_INSIDE = (0, 2)
        BPAD_RIGHT = ((2, 0), (0, 20))

        toggle_btn_off = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAED0lEQVRYCe1WTWwbRRR+M/vnv9hO7BjHpElMKSlpqBp6gRNHxAFVcKM3qgohQSqoqhQ45YAILUUVDRxAor2VAweohMSBG5ciodJUSVqa/iikaePEP4nj2Ovdnd1l3qqJksZGXscVPaylt7Oe/d6bb9/svO8BeD8vA14GvAx4GXiiM0DqsXv3xBcJU5IO+RXpLQvs5yzTijBmhurh3cyLorBGBVokQG9qVe0HgwiXLowdy9aKsY3g8PA5xYiQEUrsk93JTtjd1x3siIZBkSWQudUK4nZO1w3QuOWXV+HuP/fL85klAJuMCUX7zPj4MW1zvC0Ej4yMp/w++K2rM9b70sHBYCjo34x9bPelsgp/XJksZ7KFuwZjr3732YcL64ttEDw6cq5bVuCvgy/sje7rT0sI8PtkSHSEIRIKgCQKOAUGM6G4VoGlwiqoVd2Za9Vl8u87bGJqpqBqZOj86eEHGNch+M7otwHJNq4NDexJD+59RiCEQG8qzslFgN8ibpvZNsBifgXmFvJg459tiOYmOElzYvr2bbmkD509e1ylGEZk1Y+Ssfan18n1p7vgqVh9cuiDxJPxKPT3dfGXcN4Tp3dsg/27hUQs0qMGpRMYjLz38dcxS7Dm3nztlUAb38p0d4JnLozPGrbFfBFm79c8hA3H2AxcXSvDz7/+XtZE1kMN23hjV7LTRnKBh9/cZnAj94mOCOD32gi2EUw4FIRUMm6LGhyiik86nO5NBdGRpxYH14bbjYfJteN/OKR7UiFZVg5T27QHYu0RBxoONV9W8KQ7QVp0iXdE8fANUGZa0QAvfhhXlkQcmjJZbt631oIBnwKmacYoEJvwiuFgWncWnXAtuVBBEAoVVXWCaQZzxmYuut68b631KmoVBEHMUUrJjQLXRAQVSxUcmrKVHfjWWjC3XOT1FW5QrWpc5IJdQhDKVzOigEqS5dKHMVplnNOqrmsXqUSkn+YzWaHE9RW1FeXL7SKZXBFUrXW6jIV6YTEvMAUu0W/G3kcxPXP5ylQZs4fa6marcWvvZfJu36kuHjlc/nMSuXz+/ejxgqPFpuQ/xVude9eu39Jxu27OLvBGoMjrUN04zrNMbgVmOBZ96iPdPZmYntH5Ls76KuxL9NyoLA/brav7n382emDfHqeooXyhQmARVhSnAwNNMx5bu3V1+habun5nWdXhwJZ2C5mirTesyUR738sv7g88UQ0rEkTDlp+1wwe8Pf0klegUenYlgyg7bby75jUTITs2rhCAXXQ2vwxz84vlB0tZ0wL4NEcLX/04OrrltG1s8aOrHhk51SaK0us+n/K2xexBxljcsm1n6x/Fuv1PCWGiKOaoQCY1Vb9gWPov50+fdEqd21ge3suAlwEvA14G/ucM/AuppqNllLGPKwAAAABJRU5ErkJggg=='   
        toggle_btn_on = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAD+UlEQVRYCe1XzW8bVRCffbvrtbP+2NhOD7GzLm1VoZaPhvwDnKBUKlVyqAQ3/gAkDlWgPeVQEUCtEOIP4AaHSI0CqBWCQyXOdQuRaEFOk3g3IMWO46+tvZ+PeZs6apq4ipON1MNafrvreTPzfvub92bGAOEnZCBkIGQgZOClZoDrh25y5pdjruleEiX+A+rCaQo05bpuvJ/+IHJCSJtwpAHA/e269g8W5RbuzF6o7OVjF8D3Pr4tSSkyjcqfptPDMDKSleW4DKIggIAD5Yf+Oo4DNg6jbUBlvWLUNutAwZu1GnDjzrcXzGcX2AHw/emFUV6Sfk0pqcKpEydkKSo9q3tkz91uF5aWlo1Gs/mYc+i7tz4//19vsW2AU9O381TiioVCQcnlRsWeQhD3bJyH1/MiFLICyBHiuzQsD1arDvypW7DR9nzZmq47q2W95prm+I9fXfqXCX2AF2d+GhI98Y8xVX0lnxvl2UQQg0csb78ag3NjEeD8lXZ7pRTgftmCu4864OGzrq+5ZU0rCa3m+NzXlzvoAoB3+M+SyWQuaHBTEzKMq/3BMbgM+FuFCDBd9kK5XI5PJBKqLSev+POTV29lKB8rT0yMD0WjUSYLZLxzNgZvIHODOHuATP72Vwc6nQ4Uiw8MUeBU4nHS5HA6TYMEl02wPRcZBJuv+ya+UCZOIBaLwfCwQi1Mc4QXhA+PjWRkXyOgC1uIhW5Qd8yG2TK7kSweLcRGKKVnMNExWWBDTQsH9qVmtmzjiThQDs4Qz/OUSGTwcLwIQTLW58i+yOjpXDLqn1tgmDzXzRCk9eDenjo9yhvBmlizrB3V5dDrNTuY0A7opdndStqmaQLPC1WCGfShYRgHdLe32UrV3ntiH9LliuNrsToNlD4kruN8v75eafnSgC6Luo2+B3fGKskilj5muV6pNhk2Qqg5v7lZ51nBZhNBjGrbxfI1+La5t2JCzfD8RF1HTBGJXyDzs1MblONulEqPDVYXgwDIfNx91IUVbAbY837GMur+/k/XZ75UWmJ77ou5mfM1/0x7vP1ls9XQdF2z9uNsPzosXPNFA5m0/EX72TBSiqsWzN8z/GZB08pWq9VeEZ+0bjKb7RTD2i1P4u6r+bwypo5tZUumEcDAmuC3W8ezIqSGfE6g/sTd1W5p5bKjaWubrmWd29Fu9TD0GlYlmTx+8tTJoZeqYe2BZC1/JEU+wQR5TVEUPptJy3Fs+Vkzgf8lemqHumP1AnYoMZSwsVEz6o26i/G9Lgitb+ZmLu/YZtshfn5FZDPBCcJFQRQ+8ih9DctOFvdLIKHH6uUQnq9yhFu0bec7znZ+xpAGmuqef5/wd8hAyEDIQMjAETHwP7nQl2WnYk4yAAAAAElFTkSuQmCC'

        top_banner = [[sg.Text('Dashboard' + ' ' * 64, font='Any 20', background_color=DARK_HEADER_COLOR, text_color=WHITE_COLOR),
                    sg.Text(self.singleton .date_now , font='Any 16', background_color=DARK_HEADER_COLOR, key='-DATE-'), sg.Text(self.singleton .time_now , font='Any 16', background_color=DARK_HEADER_COLOR, key='-TIME-')]]

        top = [[sg.Text('Home Control', size=(50, 1), font='Any 20 bold', background_color=DARK_HEADER_COLOR, text_color=WHITE_COLOR)],
        # [sg.Text('Temperature (°C)', size=(20, 1), font='Any 14'), sg.Text('temp', size=(10, 1), font='Any 14', key='-TEMP-'), sg.Text('Humidity (%RH)', size=(20, 1), font='Any 14'), sg.Text('humidity', size=(10, 1), font='Any 14', key='-HUMID-')],
        [sg.Button('Exit'), sg.Button('Go')]]

        light_block = [[sg.Button(image_filename="../icons/lighton.png", key='-LIGHTS-', button_color=GRAY_BACKGROUND, border_width=0, pad=(0, 0)), sg.Text('Lights', font='Any 14', background_color=GRAY_BACKGROUND)]]

        switch_block = [[sg.Button(image_filename="../icons/switch.png", key='-SWITCHES-', border_width=0, button_color=GRAY_BACKGROUND, pad=(0, 0)), sg.Text('Switches', font='Any 14', background_color=GRAY_BACKGROUND)]]

        timer_block = [[sg.Button(image_filename="../icons/timer.png", key='-TIMER-', border_width=0, button_color=GRAY_BACKGROUND, pad=(0, 0)), sg.Text('Set Timer', font='Any 14', background_color=GRAY_BACKGROUND)]]
        
        ai_block = [[sg.Button(image_filename="../icons/assistant.png", key='-ASSISTANT-', border_width=0, button_color=GRAY_BACKGROUND, pad=(0, 0)), sg.Text('Assistant', font='Any 14', background_color=GRAY_BACKGROUND)]]
        
        # Create the light content block dynamically
        for light in self.list_lights:
            self.light_content_block.append(
                [
                    sg.Text(light.name, font="Any 14", pad=(10, 10)),  # Use dot notation
                    sg.Button(
                        image_filename="../icons/lighton.png",
                        key=f'-{str(light.id).upper()}-ON',  # Use dot notation
                        visible= True if light.state == 1 else False,  # Use dot notation
                        border_width=0,
                    ),
                    sg.Button(
                        image_filename="../icons/lightoff.png",
                        key=f'-{str(light.id).upper()}-OFF',  # Use dot notation
                        visible= True if light.state == 0 else False,  # Use dot notation
                        border_width=0,
                    ),
                ]
            )

        # Create the switch content block dynamically
        for sw in self.list_switches:
            self.switch_content_block.append(
                [
                    sg.Button(
                        '', 
                        image_data= toggle_btn_on if sw.state == 1 else toggle_btn_off, 
                        key=f'-{str(sw.id).upper()}-TOGGLE-GRAPHIC-', 
                        button_color=(sg.theme_background_color(), sg.theme_background_color()), 
                        border_width=0
                    ),
                    sg.Text(sw.name, font="Any 14", pad=(10, 10)),  # Use dot notation
                ]
            )

        timer_content_block = [[sg.Text('Set timer for devices')],
                                [sg.InputText(), sg.Button('Set Timer')]]
        
        ai_content_block = [[sg.Text('Press start to start Assistant', font='Any 14')],
                            [sg.Button(image_filename="../icons/start.png", key='-ASSISTANT-START-')],
                            [sg.Text('AI started! Say Hello to wake word...', key='-WAKE-WORD-START-', visible=False)],
                            [sg.Text('Press stop to stop Assistant', font='Any 14')],
                            [sg.Button(image_filename="../icons/stop.png", key='-ASSISTANT-STOP-')]]

        layout = [[sg.Column(top_banner, size=(960, 60), pad=(0,0), background_color=DARK_HEADER_COLOR)],
                [sg.Column(top, size=(940, 90), pad=BPAD_TOP, background_color=DARK_HEADER_COLOR)],
                [sg.Column([[sg.Column(light_block, size=(170,50), pad=BPAD_LEFT_INSIDE, background_color=GRAY_BACKGROUND)],
                            [sg.Column(switch_block, size=(170,50),  pad=BPAD_LEFT_INSIDE, background_color=GRAY_BACKGROUND)],
                            [sg.Column(timer_block, size=(170,50),  pad=BPAD_LEFT_INSIDE, background_color=GRAY_BACKGROUND)],
                            [sg.Column(ai_block, size=(170,50),  pad=BPAD_LEFT_INSIDE, background_color=GRAY_BACKGROUND)]],
                            pad=BPAD_LEFT, size=(170,320)),
                sg.Column(self.light_content_block, size=(384, 320), pad=BPAD_RIGHT, key='-TOGGLE_LIGHT_BLOCK-',visible=True),
                sg.Column(self.switch_content_block, size=(384, 320), pad=BPAD_RIGHT, key='-TOGGLE_SWITCH_BLOCK-', visible=False),
                sg.Column(timer_content_block, size=(768, 320), pad=BPAD_RIGHT, key='-TOGGLE_TIMER_BLOCK-', visible=False),
                sg.Column(ai_content_block, size=(768, 320), pad=BPAD_RIGHT, key='-TOGGLE_AI_BLOCK-', visible=False),]]

        window = sg.Window('Dashboard Control', layout, margins=(0, 0), background_color=BORDER_COLOR, no_titlebar=True, grab_anywhere=True)
        return window

    def update_time_date(self):
        now = datetime.now(IST)
        self.singleton.date_now = now.strftime("%d/%m/%Y")
        self.singleton.time_now = now.strftime("%H:%M:%S")
        self.window['-DATE-'].update(self.singleton.date_now)
        self.window['-TIME-'].update(self.singleton.time_now)

    # def update_ip_address(self):
    #     hostname = socket.gethostname()
    #     ip_address = socket.gethostbyname(hostname)
    #     self.window['-IP-'].update(ip_address)

    def update_block(self, key):
        cases = {
                '-TOGGLE_LIGHT_BLOCK-': lambda: (
                    self.window[key].update(visible=self.toggle_light_block),
                    self.window['-TOGGLE_SWITCH_BLOCK-'].update(visible=self.toggle_switch_block),
                    self.window['-TOGGLE_TIMER_BLOCK-'].update(visible=self.toggle_timer_block),
                    self.window['-TOGGLE_AI_BLOCK-'].update(visible=self.toggle_ai_block),
                ),
                '-TOGGLE_SWITCH_BLOCK-': lambda: (
                    self.window[key].update(visible=self.toggle_switch_block),
                    self.window['-TOGGLE_LIGHT_BLOCK-'].update(visible=self.toggle_light_block),
                    self.window['-TOGGLE_TIMER_BLOCK-'].update(visible=self.toggle_timer_block),
                    self.window['-TOGGLE_AI_BLOCK-'].update(visible=self.toggle_ai_block),
                ),
                '-TOGGLE_TIMER_BLOCK-': lambda: (
                    self.window[key].update(visible=self.toggle_timer_block),
                    self.window['-TOGGLE_SWITCH_BLOCK-'].update(visible=self.toggle_switch_block),
                    self.window['-TOGGLE_LIGHT_BLOCK-'].update(visible=self.toggle_light_block),
                    self.window['-TOGGLE_AI_BLOCK-'].update(visible=self.toggle_ai_block),
                ),
                '-TOGGLE_AI_BLOCK-': lambda: (
                    self.window[key].update(visible=self.toggle_ai_block),
                    self.window['-TOGGLE_SWITCH_BLOCK-'].update(visible=self.toggle_switch_block),
                    self.window['-TOGGLE_LIGHT_BLOCK-'].update(visible=self.toggle_light_block),
                    self.window['-TOGGLE_TIMER_BLOCK-'].update(visible=self.toggle_timer_block),
                )
            }

        cases.get(key, lambda: (
            self.window[key].update(visible=self.toggle_light_block),
            self.window['-TOGGLE_SWITCH_BLOCK-'].update(visible=self.toggle_switch_block),
            self.window['-TOGGLE_TIMER_BLOCK-'].update(visible=self.toggle_timer_block),
            self.window['-TOGGLE_AI_BLOCK-'].update(visible=self.toggle_ai_block),
        ))()
    
    def create_new_device_content_block(self, device, device_type):
        if device_type == 'BLE':
            for light in self.list_lights:
                self.light_content_block.clear()
                self.light_content_block.append(
                    [
                        sg.Text(light.name, font="Any 14", pad=(10, 10)),  # Use dot notation
                        sg.Button(
                            image_filename="../icons/lighton.png",
                            key=f'-{str(light.id).upper()}-ON',  # Use dot notation
                            visible= True if light.state == 1 else False,  # Use dot notation
                            border_width=0,
                        ),
                        sg.Button(
                            image_filename="../icons/lightoff.png",
                            key=f'-{str(light.id).upper()}-OFF',  # Use dot notation
                            visible= True if light.state == 0 else False,  # Use dot notation
                            border_width=0,
                        ),
                    ]
                )
            self.window.extend_layout(self.window['-TOGGLE_LIGHT_BLOCK-'], self.light_content_block)
            # self.window['-TOGGLE_LIGHT_BLOCK-'].update(self.light_content_block)
        else:
            for sw in self.list_switches:
                self.switch_content_block.clear()
                self.switch_content_block.append(
                    [
                        sg.Button(
                            '', 
                            image_data= self.toggle_btn_on if device.state == 1 else self.toggle_btn_off, 
                            key=f'-{str(device.id).upper()}-TOGGLE-GRAPHIC-', 
                            button_color=(sg.theme_background_color(), sg.theme_background_color()), 
                            border_width=0
                        ),
                        sg.Text(device.name, font="Any 14", pad=(10, 10)),  # Use dot notation
                    ]
                )
            self.window.extend_layout(self.window['-TOGGLE_SWITCH_BLOCK-'], self.switch_content_block)
            # self.window['-TOGGLE_SWITCH_BLOCK-'].update(self.light_content_block)
        self.window.refresh() 
        
    def remove_device_content_block(self, device, device_type):
        if device_type == 'BLE':
            self.light_content_block = [block for block in self.light_content_block if block[0].DisplayText != device.name]
        else:
            self.switch_content_block = [block for block in self.switch_content_block if block[0].DisplayText != device.name]
        self.window.refresh()  

    def send_command_to_master(self, device_id, action, service):
        print("send command to master", device_id, action, service)
        command = hubscreen_pb2.Command()
        print(action)
        command.action = 'turn on' if action else 'turn off'
        command.receiver = service
        command.sender = 'hubscreen'
        if service == 'BLE':
            light = hubscreen_pb2.Led_t()
            light.name = f'Light - {device_id}'
            light.id = device_id
            light.state = 1 if action else 0
            command.led_device.append(light)
        else:
            sw = hubscreen_pb2.Switch_t()
            sw.name =f'Switch - {device_id}'
            sw.id = device_id
            sw.state = 1 if action else 0
            command.sw_device.append(sw)

        # Connect to Master Service
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            # Connect to the Master Service's Unix Domain Socket
            client_socket.connect(GUI_SEND_SERVICE_SOCKET)

            # Serialize the command using Protocol Buffers
            command_str = command.SerializeToString()

            # Send the serialized command to the Master Service
            client_socket.sendall(command_str)

        except Exception as e:
            print(f"Error communicating with Master Service: {e}")

        finally:
            # Close the client socket
            client_socket.close()

        # Receive response
        # data = client_socket.recv(1024)

        # response = hubscreen_pb2.Response()
        # response.ParseFromString(data)
        # client_socket.close()
        


