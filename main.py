import speech_recognition as sr
import pyttsx3
import requests
import json
import pyaudio

# Initialize the speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# LM Studio API endpoint (adjust if necessary)
API_URL = "http://localhost:1234/v1/chat/completions"

# Patch the Microphone class
class PatchedMicrophone(sr.Microphone):
    @classmethod
    def get_pyaudio(cls):
        return pyaudio

sr.Microphone = PatchedMicrophone

def transcribe_audio():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return None
        except sr.RequestError:
            print("Sorry, there was an error with the speech recognition service.")
            return None

def get_llama_response(prompt):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"Error: Unable to get response from LLaMA model. {str(e)}"

def speak_response(text):
    engine.say(text)
    engine.runAndWait()

def main():
    print("Audio Assistant is ready. Speak your question!")
    
    while True:
        question = transcribe_audio()
        if question:
            print("Getting response from LLaMA...")
            response = get_llama_response(question)
            print(f"LLaMA: {response}")
            speak_response(response)

if __name__ == "__main__":
    main()