import os
import sys
import json
import time
import cohere
from dotenv import load_dotenv
from vosk import Model, KaldiRecognizer
import pyaudio

load_dotenv()
# openai.api_key = os.getenv('OPENAI_API_KEY')
co = cohere.Client(os.getenv('COHERE_API_KEY'))

# Path to Vosk model
model_path = "/home/thuhuong/vosk-model-small-en-us-0.15"

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
            response = co.chat(
                message=prompt
            )
            print(f"OpenAI response: {response}")

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
