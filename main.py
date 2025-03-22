import speech_recognition as sr
from gtts import gTTS
import pygame
import time

# Step 1: Convert Audio (WAV) to Text
def audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)  # Load the audio file
        try:
            text = recognizer.recognize_google(audio, language="en")  # Change "en" to "sw" for Swahili
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "Could not request results"

# Step 2: Text-to-Speech (TTS)
def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang="en")  # Change "en" to "sw" for Swahili
    tts.save(output_file)
    print(f"Audio saved to {output_file}")

# Step 3: Play Audio using pygame
def play_audio(file):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # Wait for the audio to finish playing
        time.sleep(1)

# Example usage
audio_file = "Acts_1-1.wav"
output_file = "output_audio.mp3"

# Convert audio to text
text = audio_to_text(audio_file)
print("Extracted Text:", text)

# Convert text to speech
text_to_speech(text, output_file)

# Play the generated audio
play_audio(output_file)