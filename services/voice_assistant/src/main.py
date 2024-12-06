import os
import re
import sys
import json
import time
import socket
import cohere
from dotenv import load_dotenv
from vosk import Model, KaldiRecognizer
import pyaudio
import hubscreen_pb2

load_dotenv()
# openai.api_key = os.getenv('OPENAI_API_KEY')
co = cohere.Client(os.getenv('COHERE_API_KEY'))

# Path to Vosk model
model_path = "/home/thuhuong/gateway/vosk-model-small-en-us-0.15"
AI_SERVICE_SOCKET = "/tmp/ai_socket"

number_map = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8", 
    "nine": "9",
    "zero": "0"
}

commands = {
    1: "turn on the light one",
    2: "turn off the light one",
    3: "turn on the light two",
    4: "turn on the light to",
    5: "turn on the light too",
    6: "turn off the light two",
    7: "turn off the light to",
    8: "turn off the light too",
    9: "turn on the light three",
    10: "turn off the light three",
    11: "lower the window one",
    12: "higher the window one",
    13: "lower the window to",
    14: "lower the window too",
    15: "higher the window to",
    16: "higher the window too",
}

class AIVoiceAssistant:
    def __init__(self):
        # Load the Vosk model
        if not os.path.exists(model_path):
            print(f"Please download the model from https://alphacephei.com/vosk/models and unpack it as {model_path}")
            sys.exit(1)

        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
        self.stream.start_stream()

    def send_command_to_master (self, action, device_id, device_name, type):

        command = hubscreen_pb2.Command()
        command.action = action
        command.service = "MQTT"

        if type == 'BLE':
            light = hubscreen_pb2.Led_t()
            light.id = device_id
            light.name = device_name
            light.state = 1 if action == "turn on" else 0
            command.led_device.append(light)
            
        else:
            sw = hubscreen_pb2.Switch_t()
            sw.id = device_id
            sw.name = device_name
            sw.state = 1 if action == "turn on" else 0
            command.sw_device.append(sw)
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            client_socket.connect(AI_SERVICE_SOCKET)
            command_str = command.SerializeToString()
            client_socket.sendall(command_str)
            print('Sending successfully')

        except Exception as e:
            print(f"Error communicating with Master: {e}")

        finally:
            client_socket.close()

        self.listen_for_command()


    def listen_for_wake_word(self):
        print("Listening for wake word...")
        try:
            while True:
                data = self.stream.read(4096)
                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    text = json.loads(result)['text']
                    print(f"Recognized Text: {text}")
                    if "hello" in text.lower():
                        print("Wake word detected.")
                        self.listen_for_command()
                        break

        except KeyboardInterrupt:
            print("Stopping...")

        finally:
            self.cleanup()

    def listen_for_command(self):
        print("Listening for your command...")
        start_time = time.time()
        try:
            while True:
                data = self.stream.read(4096)
                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    command = json.loads(result)['text']
                    print(f"Recognized Command: {command}")

                    # pattern = r'(turn on|turn off)\s+(the\s)?(light|switch)\s*(\d+|one|two|three|four|five|six|seven|eight|nine|zero)'
                    # match = re.search(pattern, command, re.IGNORECASE)
                    if command in commands.values():
                        for key, value in commands.items():
                            if value == command:
                                print(f"Matching.....: {key}")
                                if key == 1:
                                    self.send_command_to_master("turn on", 4, "Light 1", "MQTT")
                                elif key == 2:
                                    self.send_command_to_master("turn off", 4, "Light 1", "MQTT")
                                elif key == 3 | key == 4 | key == 5:
                                    self.send_command_to_master("turn on", 5, "Light 2", "MQTT")
                                elif key == 6 | key == 7 | key == 8:
                                    self.send_command_to_master("turn off", 5, "Light 2", "MQTT")
                                elif key == 9:
                                    self.send_command_to_master("turn on", 6, "Light 3", "MQTT")
                                elif key == 10:
                                    self.send_command_to_master("turn off", 6, "Light 3", "MQTT")
                                elif key == 11:
                                    self.send_command_to_master("turn off", 1, "Window 1", "BLE")
                                elif key == 12:
                                    self.send_command_to_master("turn on", 1, "Window 1", "BLE")
                                elif key == 13 | key == 14:
                                    self.send_command_to_master("turn off", 2, "Window 2", "BLE")
                                elif key == 15 | key == 16:
                                    self.send_command_to_master("turn on", 2, "Window 2", "BLE")
                                else:
                                    print("No matching command")
                                break
                            

                    # if match:
                    #     action = match.group(1)
                    #     device_type = match.group(3)
                    #     device_number = match.group(4).lower()

                    #     # Convert spelled-out numbers to digits
                    #     if device_number in number_map:
                    #         device_number = number_map[device_number]
                    #     self.send_command_to_master(action, device_type, device_number)
                    # else:
                    #     self.get_openai_response(command)
                    # break
                if time.time() - start_time > 10:
                    print('No command found, back to sleep')
                    self.listen_for_command()
                    break

        except KeyboardInterrupt:
            print("Stopping...")

    def get_openai_response(self, prompt):
        try:
            print(f"You said: {prompt}")

            # Send input to OpenAI API
            # response = openai.ChatCompletion.create(
            #     model="gpt-4o-mini-2024-07-18",
            #     messages=[{"role": "user", "content": prompt}]
            # )
            # response_text = response.choices[0].message.content
            # response = co.chat(
            #     message=prompt
            # )
            # print(f"OpenAI response: {response}")

            # After response, listen for the wake word again
            self.listen_for_wake_word()

        except Exception as e:
            print(f"Error: {e}")
            self.listen_for_wake_word()

    def cleanup(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

if __name__ == "__main__":
    assistant = AIVoiceAssistant()
    assistant.listen_for_wake_word()
