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
sys.path.append('../')  # This adds the parent directory to the path
from protobuf import hubscreen_pb2

load_dotenv()
# openai.api_key = os.getenv('OPENAI_API_KEY')
co = cohere.Client(os.getenv('COHERE_API_KEY'))

# Path to Vosk model
model_path = "/home/thuhuong/vosk-model-small-en-us-0.15"
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

    def send_command_to_master (self, action, device_type, device_number):

        command = hubscreen_pb2.Command()
        command.action = action
        command.service = "MQTT"

        if device_type == 'light':
            light = hubscreen_pb2.Led_t()
            light.id = f"{device_type}-{device_number}"
            light.state = True if action == "turn on" else False
            command.led_device.append(light)
            
        else:
            sw = hubscreen_pb2.Switch_t()
            sw.id = f("{device_type}-{device_number}")
            sw.state = True if action == "turn on" else False
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

                    pattern = r'(turn on|turn off)\s+(the\s)?(light|switch)\s*(\d+|one|two|three|four|five|six|seven|eight|nine|zero)'
                    match = re.search(pattern, command, re.IGNORECASE)

                    if match:
                        print("matching...")
                        action = match.group(1)
                        device_type = match.group(3)
                        device_number = match.group(4).lower()

                        # Convert spelled-out numbers to digits
                        if device_number in number_map:
                            device_number = number_map[device_number]
                        self.send_command_to_master(action, device_type, device_number)
                    else:
                        self.get_openai_response(command)
                    break
                if time.time() - start_time > 5:
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
