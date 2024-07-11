import PySimpleGUI as sg
import time
from datetime import datetime
import pytz

from server.mqtt.pub_client import publish_single_message
from sensor.sht30 import read_sht30_data
# from server.ble.ble_api import get_characteristic_by_uuid

IST = pytz.timezone('Asia/Saigon')

class Singleton( object ):
    def __new__( cls ):
        if not hasattr( cls, 'instance' ):
            cls .instance = super( Singleton, cls ) .__new__( cls )
        return cls .instance
SingletonObj = Singleton()

def update_clock():
    print('Update\n')
    raw_TS = datetime.now(IST)
    SingletonObj .date_now = raw_TS.strftime('%d %b %Y')
    SingletonObj .time_now = raw_TS.strftime('%H:%M %p')

class InterfaceGraphic: 
    def __init__(self):
        pysimplegui_user_settings = sg.UserSettings()
        temp, humidity = read_sht30_data()
        theme_dict = {'BACKGROUND': '#0C0C0C',
                    'TEXT': '#FFFFFF',
                    'INPUT': '#F2EFE8',
                    'TEXT_INPUT': '#0C0C0C',
                    'SCROLL': '#F2EFE8',
                    'BUTTON': ('#0C0C0C', '#C2D4D8'),
                    'PROGRESS': ('#FFFFFF', '#C7D5E0'),
                    'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0}

        # sg.theme_add_new('Dashboard', theme_dict)     # if using 4.20.0.1+
        sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
        sg.theme('Dashboard')

        BORDER_COLOR = '#C7D5E0'
        DARK_HEADER_COLOR = '#1B2838'
        BLACK_BACKGROUND = '#000000'
        GRAY_BACKGROUND = '#858585'
        BPAD_TOP = ((10, 10), (10, 5))
        BPAD_LEFT = ((10, 0), (0, 20))
        BPAD_LEFT_INSIDE = (0, 2)
        BPAD_RIGHT = ((2, 0), (0, 20))

        toggle_btn_off = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAED0lEQVRYCe1WTWwbRRR+M/vnv9hO7BjHpElMKSlpqBp6gRNHxAFVcKM3qgohQSqoqhQ45YAILUUVDRxAor2VAweohMSBG5ciodJUSVqa/iikaePEP4nj2Ovdnd1l3qqJksZGXscVPaylt7Oe/d6bb9/svO8BeD8vA14GvAx4GXiiM0DqsXv3xBcJU5IO+RXpLQvs5yzTijBmhurh3cyLorBGBVokQG9qVe0HgwiXLowdy9aKsY3g8PA5xYiQEUrsk93JTtjd1x3siIZBkSWQudUK4nZO1w3QuOWXV+HuP/fL85klAJuMCUX7zPj4MW1zvC0Ej4yMp/w++K2rM9b70sHBYCjo34x9bPelsgp/XJksZ7KFuwZjr3732YcL64ttEDw6cq5bVuCvgy/sje7rT0sI8PtkSHSEIRIKgCQKOAUGM6G4VoGlwiqoVd2Za9Vl8u87bGJqpqBqZOj86eEHGNch+M7otwHJNq4NDexJD+59RiCEQG8qzslFgN8ibpvZNsBifgXmFvJg459tiOYmOElzYvr2bbmkD509e1ylGEZk1Y+Ssfan18n1p7vgqVh9cuiDxJPxKPT3dfGXcN4Tp3dsg/27hUQs0qMGpRMYjLz38dcxS7Dm3nztlUAb38p0d4JnLozPGrbFfBFm79c8hA3H2AxcXSvDz7/+XtZE1kMN23hjV7LTRnKBh9/cZnAj94mOCOD32gi2EUw4FIRUMm6LGhyiik86nO5NBdGRpxYH14bbjYfJteN/OKR7UiFZVg5T27QHYu0RBxoONV9W8KQ7QVp0iXdE8fANUGZa0QAvfhhXlkQcmjJZbt631oIBnwKmacYoEJvwiuFgWncWnXAtuVBBEAoVVXWCaQZzxmYuut68b631KmoVBEHMUUrJjQLXRAQVSxUcmrKVHfjWWjC3XOT1FW5QrWpc5IJdQhDKVzOigEqS5dKHMVplnNOqrmsXqUSkn+YzWaHE9RW1FeXL7SKZXBFUrXW6jIV6YTEvMAUu0W/G3kcxPXP5ylQZs4fa6marcWvvZfJu36kuHjlc/nMSuXz+/ejxgqPFpuQ/xVude9eu39Jxu27OLvBGoMjrUN04zrNMbgVmOBZ96iPdPZmYntH5Ls76KuxL9NyoLA/brav7n382emDfHqeooXyhQmARVhSnAwNNMx5bu3V1+habun5nWdXhwJZ2C5mirTesyUR738sv7g88UQ0rEkTDlp+1wwe8Pf0klegUenYlgyg7bby75jUTITs2rhCAXXQ2vwxz84vlB0tZ0wL4NEcLX/04OrrltG1s8aOrHhk51SaK0us+n/K2xexBxljcsm1n6x/Fuv1PCWGiKOaoQCY1Vb9gWPov50+fdEqd21ge3suAlwEvA14G/ucM/AuppqNllLGPKwAAAABJRU5ErkJggg=='   
        toggle_btn_on = b'iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAD+UlEQVRYCe1XzW8bVRCffbvrtbP+2NhOD7GzLm1VoZaPhvwDnKBUKlVyqAQ3/gAkDlWgPeVQEUCtEOIP4AaHSI0CqBWCQyXOdQuRaEFOk3g3IMWO46+tvZ+PeZs6apq4ipON1MNafrvreTPzfvub92bGAOEnZCBkIGQgZOClZoDrh25y5pdjruleEiX+A+rCaQo05bpuvJ/+IHJCSJtwpAHA/e269g8W5RbuzF6o7OVjF8D3Pr4tSSkyjcqfptPDMDKSleW4DKIggIAD5Yf+Oo4DNg6jbUBlvWLUNutAwZu1GnDjzrcXzGcX2AHw/emFUV6Sfk0pqcKpEydkKSo9q3tkz91uF5aWlo1Gs/mYc+i7tz4//19vsW2AU9O381TiioVCQcnlRsWeQhD3bJyH1/MiFLICyBHiuzQsD1arDvypW7DR9nzZmq47q2W95prm+I9fXfqXCX2AF2d+GhI98Y8xVX0lnxvl2UQQg0csb78ag3NjEeD8lXZ7pRTgftmCu4864OGzrq+5ZU0rCa3m+NzXlzvoAoB3+M+SyWQuaHBTEzKMq/3BMbgM+FuFCDBd9kK5XI5PJBKqLSev+POTV29lKB8rT0yMD0WjUSYLZLxzNgZvIHODOHuATP72Vwc6nQ4Uiw8MUeBU4nHS5HA6TYMEl02wPRcZBJuv+ya+UCZOIBaLwfCwQi1Mc4QXhA+PjWRkXyOgC1uIhW5Qd8yG2TK7kSweLcRGKKVnMNExWWBDTQsH9qVmtmzjiThQDs4Qz/OUSGTwcLwIQTLW58i+yOjpXDLqn1tgmDzXzRCk9eDenjo9yhvBmlizrB3V5dDrNTuY0A7opdndStqmaQLPC1WCGfShYRgHdLe32UrV3ntiH9LliuNrsToNlD4kruN8v75eafnSgC6Luo2+B3fGKskilj5muV6pNhk2Qqg5v7lZ51nBZhNBjGrbxfI1+La5t2JCzfD8RF1HTBGJXyDzs1MblONulEqPDVYXgwDIfNx91IUVbAbY837GMur+/k/XZ75UWmJ77ou5mfM1/0x7vP1ls9XQdF2z9uNsPzosXPNFA5m0/EX72TBSiqsWzN8z/GZB08pWq9VeEZ+0bjKb7RTD2i1P4u6r+bwypo5tZUumEcDAmuC3W8ezIqSGfE6g/sTd1W5p5bKjaWubrmWd29Fu9TD0GlYlmTx+8tTJoZeqYe2BZC1/JEU+wQR5TVEUPptJy3Fs+Vkzgf8lemqHumP1AnYoMZSwsVEz6o26i/G9Lgitb+ZmLu/YZtshfn5FZDPBCcJFQRQ+8ih9DctOFvdLIKHH6uUQnq9yhFu0bec7znZ+xpAGmuqef5/wd8hAyEDIQMjAETHwP7nQl2WnYk4yAAAAAElFTkSuQmCC'

        top_banner = [[sg.Text('Dashboard' + ' ' * 64, font='Any 20', background_color=DARK_HEADER_COLOR),
                    sg.Text(SingletonObj .date_now , font='Any 20', background_color=DARK_HEADER_COLOR, key='-DATE-'), sg.Text(SingletonObj .time_now , font='Any 20', background_color=DARK_HEADER_COLOR, key='-TIME-')]]

        top = [[sg.Text('Home Control', size=(50, 1), font='Any 20')],
        [sg.Text('Temperature (°C)', size=(10, 1), font='Any 14'), sg.Text(temp, size=(10, 1), font='Any 14', key='-TEMP-'), sg.Text('Humidity (%RH)', size=(10, 1), font='Any 14'), sg.Text(humidity, size=(10, 1), font='Any 14', key='-HUMID-')]]

        light_block = [[sg.Button(image_filename="./icons/lighton.png", key='-LIGHTS-', button_color=GRAY_BACKGROUND, border_width=0, pad=(0, 0)), sg.Text('Lights', font='Any 14', background_color=GRAY_BACKGROUND)]]

        switch_block = [[sg.Button(image_filename="./icons/switch.png", key='-SWITCHES-', border_width=0, button_color=GRAY_BACKGROUND, pad=(0, 0)), sg.Text('Switches', font='Any 14', background_color=GRAY_BACKGROUND)]]

        timer_block = [[sg.Button(image_filename="./icons/timer.png", key='-TIMER-', border_width=0, button_color=GRAY_BACKGROUND, pad=(0, 0)), sg.Text('Set Timer', font='Any 14', background_color=GRAY_BACKGROUND)]]


        light_content_block = [
                                # Light 1
                                [sg.Text('Light 1', font='Any 14', pad=(10, 10)),
                                sg.Button(image_filename='./icons/lighton.png', key='-LIGHT-1-ON', visible=False, border_width=0, button_color='#0C0C0C'),
                                sg.Button( image_filename='./icons/lightoff.png', key='-LIGHT-1-OFF', visible=True, border_width=0, button_color='#0C0C0C')],
                                # Light 2
                                [sg.Text('Light 2', font='Any 14', pad=(10, 10)),
                                sg.Button(image_filename='./icons/lighton.png', key='-LIGHT-2-ON', visible=False, border_width=0, button_color='#0C0C0C'),
                                sg.Button( image_filename='./icons/lightoff.png', key='-LIGHT-2-OFF', visible=True, border_width=0, button_color='#0C0C0C')],
                                # Light 3
                                [sg.Text('Light 3', font='Any 14', pad=(10, 10)),
                                sg.Button(image_filename='./icons/lighton.png', key='-LIGHT-3-ON', visible=False, border_width=0, button_color='#0C0C0C'),
                                sg.Button( image_filename='./icons/lightoff.png', key='-LIGHT-3-OFF', visible=True, border_width=0, button_color='#0C0C0C')]]

        switch_content_block = [[sg.Text('Switch 1', font='Any 14'),
                                sg.Button('', image_data=toggle_btn_off, key='-SW1-TOGGLE-GRAPHIC-', button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0)],
                                [sg.Text('Switch 2', font='Any 14'),
                                sg.Button('', image_data=toggle_btn_off, key='-SW2-TOGGLE-GRAPHIC-', button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0)],
                                [sg.Text('Switch 3', font='Any 14'),
                                sg.Button('', image_data=toggle_btn_off, key='-SW3-TOGGLE-GRAPHIC-', button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0)]]

        timer_content_block = [[sg.Text('Set timer for devices')],
                                [sg.InputText(), sg.Button('Set Timer')]]

        layout = [[sg.Column(top_banner, size=(960, 60), pad=(0,0), background_color=DARK_HEADER_COLOR)],
                [sg.Column(top, size=(940, 90), pad=BPAD_TOP)],
                [sg.Column([[sg.Column(light_block, size=(170,50), pad=BPAD_LEFT_INSIDE, background_color=GRAY_BACKGROUND)],
                            [sg.Column(switch_block, size=(170,50),  pad=BPAD_LEFT_INSIDE, background_color=GRAY_BACKGROUND)],
                            [sg.Column(timer_block, size=(170,50),  pad=BPAD_LEFT_INSIDE, background_color=GRAY_BACKGROUND)]],
                            pad=BPAD_LEFT, size=(170,320), background_color=BLACK_BACKGROUND),
                sg.Column(light_content_block, size=(768, 320), pad=BPAD_RIGHT, key='-TOGGLE_LIGHT_BLOCK-', visible=True),
                sg.Column(switch_content_block, size=(768, 320), pad=BPAD_RIGHT, key='-TOGGLE_SWITCH_BLOCK-', visible=False),
                sg.Column(timer_content_block, size=(768, 320), pad=BPAD_RIGHT, key='-TOGGLE_TIMER_BLOCK-', visible=False)]]

        window = sg.Window('Dashboard PySimpleGUI-Style', layout, margins=(0, 0), background_color=BORDER_COLOR, no_titlebar=True, grab_anywhere=True)

        toggle_light_block = True
        toggle_switch_block = False
        toggle_timer_block = False

        down = sw1_graphic_off = True
        down = sw2_graphic_off = True
        down = sw3_graphic_off = True

        def update_block(key):

            cases = {
                '-TOGGLE_LIGHT_BLOCK-': lambda: (
                    window[key].update(visible=toggle_light_block),
                    window['-TOGGLE_SWITCH_BLOCK-'].update(visible=toggle_switch_block),
                    window['-TOGGLE_TIMER_BLOCK-'].update(visible=toggle_timer_block),
                ),
                '-TOGGLE_SWITCH_BLOCK-': lambda: (
                    window[key].update(visible=toggle_switch_block),
                    window['-TOGGLE_LIGHT_BLOCK-'].update(visible=toggle_light_block),
                    window['-TOGGLE_TIMER_BLOCK-'].update(visible=toggle_timer_block),
                ),
                '-TOGGLE_TIMER_BLOCK-': lambda: (
                    window[key].update(visible=toggle_timer_block),
                    window['-TOGGLE_SWITCH_BLOCK-'].update(visible=toggle_switch_block),
                    window['-TOGGLE_LIGHT_BLOCK-'].update(visible=toggle_light_block),
                ),
            }

            cases.get(key, lambda: (
                window[key].update(visible=toggle_light_block),
                window['-TOGGLE_SWITCH_BLOCK-'].update(visible=toggle_switch_block),
                window['-TOGGLE_TIMER_BLOCK-'].update(visible=toggle_timer_block),
            ))()

        while True:  # Event Loop
            event, values = window.read()
            window['-DATE-'].update(SingletonObj .date_now)
            window['-TIME-'].update(SingletonObj .time_now)
            window.refresh()
            update_clock()
            temp, humidity = read_sht30_data()
            window['-TEMP-'].update(temp)
            window['-HUMID-'].update(humidity)
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            elif event == '-LIGHTS-':
                toggle_light_block = True
                toggle_switch_block = False
                toggle_timer_block = False
                update_block('-TOGGLE_LIGHT_BLOCK-')
            elif event == '-SWITCHES-':
                toggle_light_block = False
                toggle_switch_block = True
                toggle_timer_block = False
                update_block('-TOGGLE_SWITCH_BLOCK-')
            elif event == '-TIMER-':
                toggle_light_block = False
                toggle_switch_block = False
                toggle_timer_block = True
                update_block('-TOGGLE_TIMER_BLOCK-')
            elif event == '-LIGHT-1-ON':
                    window['-LIGHT-1-ON'].update(visible=False)
                    window['-LIGHT-1-OFF'].update(visible=True)
                    publish_single_message('hub/lights', '1-0') # turn off
            elif event == '-LIGHT-1-OFF':
                    window['-LIGHT-1-OFF'].update(visible=False)
                    window['-LIGHT-1-ON'].update(visible=True)
                    publish_single_message('hub/lights', '1-1') # turn on
            elif event == '-LIGHT-2-ON':
                    window['-LIGHT-2-ON'].update(visible=False)
                    window['-LIGHT-2-OFF'].update(visible=True)
                    publish_single_message('hub/lights', '2-0')
            elif event == '-LIGHT-2-OFF':
                    window['-LIGHT-2-OFF'].update(visible=False)
                    window['-LIGHT-2-ON'].update(visible=True)
                    publish_single_message('hub/lights', '2-1')
            elif event == '-LIGHT-3-ON':
                    window['-LIGHT-3-ON'].update(visible=False)
                    window['-LIGHT-3-OFF'].update(visible=True)
                    publish_single_message('hub/lights', '3-0')
            elif event == '-LIGHT-3-OFF':
                    window['-LIGHT-3-OFF'].update(visible=False)
                    window['-LIGHT-3-ON'].update(visible=True)
                    publish_single_message('hub/lights', '3-1')
            elif event == '-SW1-TOGGLE-GRAPHIC-':   # if the graphical button that changes images
                    sw1_graphic_off = not sw1_graphic_off
                    # get_characteristic_by_uuid(sw1_graphic_off)
                    window['-SW1-TOGGLE-GRAPHIC-'].update(image_data=toggle_btn_off if sw1_graphic_off else toggle_btn_on)
            elif event == '-SW2-TOGGLE-GRAPHIC-':   # if the graphical button that changes images
                    sw2_graphic_off = not sw2_graphic_off
                    window['-SW2-TOGGLE-GRAPHIC-'].update(image_data=toggle_btn_off if sw2_graphic_off else toggle_btn_on)
            elif event == '-SW3-TOGGLE-GRAPHIC-':   # if the graphical button that changes images
                    sw3_graphic_off = not sw3_graphic_off
                    window['-SW3-TOGGLE-GRAPHIC-'].update(image_data=toggle_btn_off if sw3_graphic_off else toggle_btn_on)
            if pysimplegui_user_settings.get('-enable debugger-', False):
                print("Debugger is enabled")
        window.close()

def main():
    update_clock()
    InterfaceGraphic()

if __name__ == "__main__":
    main()