import os
import json
import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
from gtts import gTTS
import pygame
import time

# Initialize pygame for audio playback
pygame.mixer.init()

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

# Step 6: GUI Application
class AudioBibleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Audio Bible System")
        self.root.geometry("400x300")

        # Load Bible data
        self.audio_folder = "bible_audio_files"
        self.bible_data = organize_bible_data(self.audio_folder)

        # Save the organized data to a JSON file
        with open("bible_data.json", "w", encoding="utf-8") as file:
            json.dump(self.bible_data, file, ensure_ascii=False, indent=4)
        print("Bible data organized and saved to bible_data.json")

        # Load user progress
        self.last_verse = load_progress()
        if self.last_verse:
            print(f"Resuming from last played verse: {self.last_verse}")

        # GUI Components
        self.title_label = tk.Label(root, text="Enhanced Audio Bible System", font=("Arial", 16))
        self.title_label.pack(pady=10)

        self.verse_label = tk.Label(root, text="Select a Verse:", font=("Arial", 12))
        self.verse_label.pack()

        # Dropdown for verse selection
        self.verse_var = tk.StringVar()
        self.verse_dropdown = ttk.Combobox(root, textvariable=self.verse_var)
        self.verse_dropdown["values"] = list(self.bible_data.keys())
        self.verse_dropdown.pack(pady=10)

        # Play Button
        self.play_button = tk.Button(root, text="Play", command=self.play_verse)
        self.play_button.pack(pady=10)

        # Progress Label
        self.progress_label = tk.Label(root, text="", font=("Arial", 12))
        self.progress_label.pack(pady=10)

        # Exit Button
        self.exit_button = tk.Button(root, text="Exit", command=root.quit)
        self.exit_button.pack(pady=10)

    def play_verse(self):
        verse_name = self.verse_var.get()
        if verse_name in self.bible_data:
            audio_file = self.bible_data[verse_name]["audio_file"]
            text = self.bible_data[verse_name]["text"]
            self.progress_label.config(text=f"Playing {verse_name}: {text}")
            play_audio(audio_file)
            save_progress(verse_name)  # Save progress
        else:
            self.progress_label.config(text=f"Verse {verse_name} not found.")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = AudioBibleApp(root)
    root.mainloop()