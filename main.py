import os
import json
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

# Step 2: Organize Bible Audio Files
def organize_bible_data(audio_folder):
    # Create the folder if it doesn't exist
    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder)
        print(f"Created folder: {audio_folder}")

    bible_data = {}
    for filename in os.listdir(audio_folder):
        if filename.endswith(".wav"):
            verse_name = filename.replace(".wav", "")  # Extract verse/chapter name
            audio_file = os.path.join(audio_folder, filename)
            text = audio_to_text(audio_file)  # Convert audio to text
            bible_data[verse_name] = {
                "audio_file": audio_file,
                "text": text
            }
    return bible_data

# Step 3: Text-to-Speech (TTS)
def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang="en")  # Change "en" to "sw" for Swahili
    tts.save(output_file)
    print(f"Audio saved to {output_file}")

# Step 4: Play Audio using pygame
def play_audio(file):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # Wait for the audio to finish playing
        time.sleep(1)

# Step 5: Save and Load User Progress
def save_progress(verse_name):
    with open("user_progress.json", "w", encoding="utf-8") as file:
        json.dump({"last_verse": verse_name}, file, ensure_ascii=False, indent=4)

def load_progress():
    try:
        with open("user_progress.json", "r", encoding="utf-8") as file:
            return json.load(file).get("last_verse", None)
    except FileNotFoundError:
        return None

# Step 6: Main CLI Function
def main():
    audio_folder = "bible_audio_files"
    bible_data = organize_bible_data(audio_folder)

    # Save the organized data to a JSON file
    with open("bible_data.json", "w", encoding="utf-8") as file:
        json.dump(bible_data, file, ensure_ascii=False, indent=4)
    print("Bible data organized and saved to bible_data.json")

    # Load user progress
    last_verse = load_progress()
    if last_verse:
        print(f"Resuming from last played verse: {last_verse}")

    print("Welcome to the Enhanced Audio Bible System!")
    print("Available verses:", list(bible_data.keys()))

    while True:
        verse_name = input("Enter the verse name (e.g., Genesis_1_1) or 'exit' to quit: ")
        if verse_name.lower() == "exit":
            break
        if verse_name in bible_data:
            audio_file = bible_data[verse_name]["audio_file"]
            text = bible_data[verse_name]["text"]
            print(f"Playing {verse_name}: {text}")
            play_audio(audio_file)
            save_progress(verse_name)  # Save progress
        else:
            print(f"Verse {verse_name} not found.")

if __name__ == "__main__":
    main()