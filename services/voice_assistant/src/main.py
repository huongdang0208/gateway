import os
import openai
from dotenv import load_dotenv
import time
import speech_recognition as sr
import pyttsx3
import numpy as np

# Load OpenAI API key from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
model = 'gpt-4o-mini-2024-07-18'

# Set up the speech recognition and text-to-speech engines
r = sr.Recognizer()

# Initialize pyttsx3 with 'espeak' driver for Linux
engine = pyttsx3.init(driverName='espeak')

# Configure pyttsx3 properties
voice = engine.getProperty('voices')[1]
engine.setProperty('voice', voice.id)
name = "Halcyon"
greetings = [f"What's up, Master {name}?", 
             "Yeah?",
             "Well, hello there, Master of Puns and Jokes - how's it going today?",
             f"Ahoy there, Captain {name}! How's the ship sailing?",
             f"Bonjour, Monsieur {name}! Comment ça va? Wait, why the hell am I speaking French?" ]

# Listen for the wake word "Hello my assistant"
def listen_for_wake_word(source):
    print("Listening for 'Hello my assistant'...")

    while True:
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            if "Hello my assistant" in text.lower():
                print("Wake word detected.")
                engine.say(np.random.choice(greetings))
                engine.runAndWait()
                listen_and_respond(source)
                break
        except sr.UnknownValueError:
            pass

# Listen for input and respond with OpenAI API
def listen_and_respond(source):
    print("Listening...")

    while True:
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            if not text:
                continue

            # Send input to OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"{text}"}]
            ) 
            response_text = response.choices[0].message.content
            print(f"OpenAI response: {response_text}")

            # Speak the response
            engine.say(response_text)
            engine.runAndWait()

            if not audio:
                listen_for_wake_word(source)
        except sr.UnknownValueError:
            time.sleep(2)
            print("Silence found, shutting up, listening...")
            listen_for_wake_word(source)
            break
            
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            engine.say(f"Could not request results; {e}")
            engine.runAndWait()
            listen_for_wake_word(source)
            break

# Use the default microphone as the audio source
with sr.Microphone() as source:
    listen_for_wake_word(source)
