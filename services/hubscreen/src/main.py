import PySimpleGUI as sg
import threading
import asyncio
import pytz
import socket
from datetime import datetime
from protobuf import hubscreen_pb2

# Constants
MASTER_SERVICE_PORT = 5003
IST = pytz.timezone('Asia/Ho_Chi_Minh')

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
        
        # Initialize window components
        self.window = self.create_window()
        self.toggle_light_block = True
        self.toggle_switch_block = False
        self.toggle_timer_block = False
        self.sw1_graphic_off = True
        self.sw2_graphic_off = True
        self.sw3_graphic_off = True

    def create_window(self):
        # Define themes and colors
        theme_dict = {
            'BACKGROUND': '#0C0C0C',
            'TEXT': '#FFFFFF',
            'INPUT': '#F2EFE8',
            'TEXT_INPUT': '#0C0C0C',
            'SCROLL': '#F2EFE8',
            'BUTTON': ('#0C0C0C', '#C2D4D8'),
            'PROGRESS': ('#FFFFFF', '#C7D5E0'),
            'BORDER': 1,
            'SLIDER_DEPTH': 0,
            'PROGRESS_DEPTH': 0
        }
        sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
        sg.theme('Dashboard')

        # Define various blocks for GUI layout
        BORDER_COLOR = '#C7D5E0'
        DARK_HEADER_COLOR = '#1B2838'
        BLACK_BACKGROUND = '#000000'
        GRAY_BACKGROUND = '#858585'
        BPAD_TOP = ((10, 10), (10, 5))
        BPAD_LEFT = ((10, 0), (0, 20))
        BPAD_LEFT_INSIDE = (0, 2)
        BPAD_RIGHT = ((2, 0), (0, 20))

        toggle_btn_off = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAED0lEQVRYCe1WTWwbRRR+M/vnv9hO7BjHpElMKSlpqBp6gRNHxAFVcKM3qgohQSqoqhQ45YAILUUVDRxAor2VAweohMSBG5ciodJUSVqa/iikaePEP4nj2Ovdnd1l3qqJksZGXscVPaylt7Oe/d6bb9/svO8BeD8vA14GvAx4GXiiM0DqsXv3xBcJU5IO+RXpLQvs5yzTijBmhurh3cyLorBGBVokQG9qVe0HgwiXLowdy9aKsY3g8PA5xYiQEUrsk93JTtjd1x3siIZBkSWQudUK4nZO1w3QuOWXV+HuP/fL85klAJuMCUX7zPj4MW1zvC0Ej4yMp/w++K2rM9b70sHBYCjo34x9bPelsgp/XJksZ7KFuwZjr3732YcL64ttEDw6cq5bVuCvgy/sje7rT0sI8PtkSHSEIRIKgCQKOAUGM6G4VoGlwiqoVd2Za9Vl8u87bGJqpqBqZOj86eEHGNch+M7otwHJNq4NDexJD+59RiCEQG8qzslFgN8ibpvZNsBifgXmFvJg459tiOYmOElzYvr2bbmkD509e1ylGEZk1Y+Ssfan18n1p7vgqVh9cuiDxJPxKPT3dfGXcN4Tp3dsg/27hUQs0qMGpRMYjLz38dcxS7Dm3nztlUAb38p0d4JnLozPGrbFfBFm79c8hA3H2AxcXSvDz7/+XtZE1kMN23hjV7LTRnKBh9/cZnAj94mOCOD32gi2EUw4FIRUMm6LGhyiik86nO5NBdGRpxYH14bbjYfJteN/OKR7UiFZVg5T27QHYu0RBxoONV9W8KQ7QVp0iXdE8fANUGZa0QAvfhhXlkQcmjJZbt631oIBnwKmacYoEJvwiuFgWncWnXAtuVBBEAoVVXWCaQZzxmYuut68b631KmoVBEHMUUrJjQLXRAQVSxUcmrKVHfjWWjC3XOT1FW5QrWpc5IJdQhDKVzOigEqS5dKHMVplnNOqrmsXqUSkn+YzWaHE9RW1FeXL7SKZXBFUrXW6jIV6YTEvMAUu0W/G3kcxPXP5ylQZs4fa6marcWvvZfJu36kuHjlc/nMSuXz+/ejxgqPFpuQ/xVude9eu39Jxu27OLvBGoMjrUN04zrNMbgVmOBZ96iPdPZmYntH5Ls76KuxL9NyoLA/brav7n382emDfHqeooXyhQmARVhSnAwNNMx5bu3V1+habun5nWdXhwJZ2C5mirTesyUR738sv7g88UQ0rEkTDlp+1wwe8Pf0klegUenYlgyg7bby75jUTITs2rhCAXXQ2vwxz84vlB0tZ0wL4NEcLX/04OrrltG1s8aOrHhk51SaK0us+n/K2xexBxljcsm1n6x/Fuv1PCWGiKOaoQCY1Vb9gWPov50+fdEqd21ge3suAlwEvA14G/ucM/AuppqNllLGPKwAAAABJRU5ErkJggg=='
        toggle_btn_on = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAD+UlEQVRYCe1XzW8bVRCffbvrtbP+2NhOD7GzLm1VoZaPhvwDnKBUKlVyqAQ3/gAkDlWgPeVQEUCtEOIP4AaHSI0CqBWCQyXOdQuRaEFOk3g3IMWO46+tvZ+PeZs6apq4ipON1MNafrvreTPzfvub92bGAOEnZCBkIGQgZOClZoDrh25y5pdjruleEiX+A+rCaQo05bpuvJ/+IHJCSJtwpAHA/e269g8W5RbuzF6o7OVjF8D3Pr4tSSkyjcqfptPDMDKSleW4DKIggIAD5Yf+Oo4DNg6jbUBlvWLUNutAwZu1GnDjzrcXzGcX2AHw/emFUV6Sfk0pqcKpEydkKSo9q3tkz91uF5aWlo1Gs/mYc+i7tz4//19vsW2AU9O381TiioVCQcnlRsWeQhD3bJyH1/MiFLICyBHiuzQsD1arDvypW7DR9nzZmq47q2W95prm+I9fXfqXCX2AF2d+GhI98Y8xVX0lnxvl2UQQg0csb78ag3NjEeD8lXZ7pRTgftmCu4864OGzrq+5ZU0rCa3m+NzXlzvoAoB3+M+SyWQuaHBTEzKMq/3BMbgM+FuFCDBd9kK5XI5PJBKqLSev+POTV29lKB8rT0yMD0WjUSYLZLhb7LQYjofKY0aSC9gYeCL5bdlsNg4Fuc+ldVRtytrFj1YWGleoaBQtm/MBAC5aPbgHt4fsM0FgHG3ttPB5e1XCPB6eNc8S5S11AQvc+1LprVwWvExPJBDHIegCX8gShXEn8JDnl4WXvfI4CKcf3dqlB1Y+vDMO/XkU+3lYkC45Y6+y/32xveOH8GbmnctBdf2M4nH3v3PhNLpshMjHRAnMbGNF3XFz+a5WwG3m8h1rbJc4eYV+usnz6nX9/fJdAwMHDaH2XgKnJ7ny1rVnbiTnLFy/PLV8tOLp4C4sv6G4hG4NPTA/bmMjMC2UVF1QNKEQ/AyeD8lS6nqlklUHz0nZaQjl2IkZlwZjU4/F1PaFRqtzN7bPw5A9eWwn+HmjBBFLiOgCx8vGCxv5/IFZqP7bz/nZjht/nAYPHVq6dt/TpFItUB6vpZbrdb21h/l6JcAmH6HrCbcnFGxsyMPCm08wV3s5x2L3S/mUQq7BeALa5cYzxaPEng7OVBRVEI3AU1beVD9oV8Bx8Q2KhEXwWzzRRG4eByZhCEn3SVJuaZ4NrN5Qog6yygh2V1ccjKywWIPp+q8gBRdVCZhtgJY3EG4m6qPl0c3AK2LYAYMy08W2tRCN90Fq6no0gNh6u2cCDIcTh4EBERcJhN5F2rjqFgoJ4CRI2d7sAFuBq40fqIRR1Vb9wUgSaODl4Xx7Ut8G3T3wIdnfmN1gdMj8cHY90ptGbL1lmNl1cUxMDF4nvJpgF/NBrgCeiThsFIdElRaNUu4ev1FW0oTpOc9KlLVozH57m5E3v7thMTKyGpl3fP32naS/sAToFNgU/azOWlcfzyM3tFM/Oyvn/9gtmSYyLDYr4IwAkMJoQeR6qYpgn8zPsbx5/AKuFh4TEEzLwJ20ejPfOjC14hUCg1mZTMBuPtKPYFfHdx1eyE8M3jAAOCr16OC7MFpkEr2hwi65u03cuLrFYa0yxhxud6E+VPjU3aZWTsNHhOEI3SSTG+fi5Qbi2zKxKmPOeX2Og5PEz/WhN0ewqg9dwlq1L+CrZtPtbE6TyJkqcDL1hOVqlt0vVV1VZ5rfwG8ED5pBoLSeWAAAAABJRU5ErkJggg=='

        # Define the layout of the GUI
        layout = [
            [sg.Text('Hub Screen', font='Any 20', background_color=BLACK_BACKGROUND)],
            [sg.Text('Date: ', size=(10, 1), background_color=BLACK_BACKGROUND),
             sg.Text('', key='-DATE-', size=(20, 1), background_color=BLACK_BACKGROUND)],
            [sg.Text('Time: ', size=(10, 1), background_color=BLACK_BACKGROUND),
             sg.Text('', key='-TIME-', size=(20, 1), background_color=BLACK_BACKGROUND)],
            [sg.Text('IP Address: ', size=(10, 1), background_color=BLACK_BACKGROUND),
             sg.Text('', key='-IP-', size=(20, 1), background_color=BLACK_BACKGROUND)],
            [sg.Image(data=toggle_btn_on, key='-TOGGLE-', enable_events=True),
             sg.Text('SW1', size=(4, 1), background_color=BLACK_BACKGROUND),
             sg.Text('ON', size=(3, 1), key='-SW1_STATUS-', background_color=BLACK_BACKGROUND),
             sg.Button('Timer', size=(10, 1), key='-SW1_TIMER-', button_color=GRAY_BACKGROUND)],
            [sg.Image(data=toggle_btn_off, key='-TOGGLE2-', enable_events=True),
             sg.Text('SW2', size=(4, 1), background_color=BLACK_BACKGROUND),
             sg.Text('OFF', size=(3, 1), key='-SW2_STATUS-', background_color=BLACK_BACKGROUND),
             sg.Button('Timer', size=(10, 1), key='-SW2_TIMER-', button_color=GRAY_BACKGROUND)],
            [sg.Image(data=toggle_btn_off, key='-TOGGLE3-', enable_events=True),
             sg.Text('SW3', size=(4, 1), background_color=BLACK_BACKGROUND),
             sg.Text('OFF', size=(3, 1), key='-SW3_STATUS-', background_color=BLACK_BACKGROUND),
             sg.Button('Timer', size=(10, 1), key='-SW3_TIMER-', button_color=GRAY_BACKGROUND)],
            [sg.Text('Light Control', font='Any 18', background_color=BLACK_BACKGROUND)],
            [sg.Button('Toggle Light', size=(15, 1), key='-TOGGLE_LIGHT-', button_color=GRAY_BACKGROUND)]
        ]
        return sg.Window('Hub Screen', layout, finalize=True, keep_on_top=True, location=(0, 0))

    def update_time_date(self):
        now = datetime.now(IST)
        self.singleton.date_now = now.strftime("%d/%m/%Y")
        self.singleton.time_now = now.strftime("%H:%M:%S")
        self.window['-DATE-'].update(self.singleton.date_now)
        self.window['-TIME-'].update(self.singleton.time_now)

    def update_ip_address(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        self.window['-IP-'].update(ip_address)

    def toggle_switch(self, switch_num):
        if switch_num == 1:
            if self.sw1_graphic_off:
                self.window['-TOGGLE-'].update(data=self.toggle_btn_on)
                self.window['-SW1_STATUS-'].update('ON')
                self.sw1_graphic_off = False
            else:
                self.window['-TOGGLE-'].update(data=self.toggle_btn_off)
                self.window['-SW1_STATUS-'].update('OFF')
                self.sw1_graphic_off = True
        elif switch_num == 2:
            if self.sw2_graphic_off:
                self.window['-TOGGLE2-'].update(data=self.toggle_btn_on)
                self.window['-SW2_STATUS-'].update('ON')
                self.sw2_graphic_off = False
            else:
                self.window['-TOGGLE2-'].update(data=self.toggle_btn_off)
                self.window['-SW2_STATUS-'].update('OFF')
                self.sw2_graphic_off = True
        elif switch_num == 3:
            if self.sw3_graphic_off:
                self.window['-TOGGLE3-'].update(data=self.toggle_btn_on)
                self.window['-SW3_STATUS-'].update('ON')
                self.sw3_graphic_off = False
            else:
                self.window['-TOGGLE3-'].update(data=self.toggle_btn_off)
                self.window['-SW3_STATUS-'].update('OFF')
                self.sw3_graphic_off = True

    def toggle_light(self):
        self.toggle_light_block = not self.toggle_light_block
        if self.toggle_light_block:
            self.window['-TOGGLE_LIGHT-'].update(button_color=('white', 'green'))
        else:
            self.window['-TOGGLE_LIGHT-'].update(button_color=('white', 'red'))

    def run(self):
        self.update_ip_address()
        while True:
            event, _ = self.window.read(timeout=1000)
            self.update_time_date()
            if event == sg.WIN_CLOSED:
                break
            elif event == '-TOGGLE-':
                self.toggle_switch(1)
            elif event == '-TOGGLE2-':
                self.toggle_switch(2)
            elif event == '-TOGGLE3-':
                self.toggle_switch(3)
            elif event == '-TOGGLE_LIGHT-':
                self.toggle_light()
            elif event == '-SW1_TIMER-':
                self.timer_switch(1)
            elif event == '-SW2_TIMER-':
                self.timer_switch(2)
            elif event == '-SW3_TIMER-':
                self.timer_switch(3)

    def timer_switch(self, switch_num):
        # Implement timer logic for switches
        pass

# Network Communication Class
class NetworkCommunication:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.running = True
        self.server_task = None
        self.gui = InterfaceGraphic()

    async def handle_client(self, reader, writer):
        data = await reader.read(1024)
        address = writer.get_extra
