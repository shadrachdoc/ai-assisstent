import speech_recognition as sr
import pyttsx3
import requests
import json
import pyaudio
import keyboard
import time
import io
import wave

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
    print("Audio Assistant is ready. Press and hold the space bar to ask a question!")
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    
    while True:
        print("Press and hold the space bar to ask a question...")
        keyboard.wait('space')  # Wait for space bar to be pressed
        print("Listening... (Release space bar when done speaking)")
        
        frames = []
        
        # Record audio while space bar is pressed
        while keyboard.is_pressed('space'):
            data = stream.read(1024)
            frames.append(data)
        
        print("Processing your question...")
        
        # Save the recorded audio to a WAV file in memory
        audio_data = io.BytesIO()
        wf = wave.open(audio_data, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Rewind the stream to the beginning
        audio_data.seek(0)
        
        # Create AudioData object
        audio = sr.AudioData(audio_data.read(), 16000, 2)
        
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            if text:
                print("Getting response from LLaMA...")
                response = get_llama_response(text)
                print(f"LLaMA: {response}")
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
        except sr.RequestError:
            print("Sorry, there was an error with the speech recognition service.")
        
        print("\nPress space bar when you're ready for the next question...")
        keyboard.wait('space')
        keyboard.wait('space', True)  # Wait for space bar to be released

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    main()