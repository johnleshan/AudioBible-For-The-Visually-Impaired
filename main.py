import os
import json
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import speech_recognition as sr
from gtts import gTTS
import pygame
import time
from PIL import Image, ImageTk  # For icons

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

# Step 4: Save and Load User Progress
def save_progress(verse_name):
    with open("user_progress.json", "w", encoding="utf-8") as file:
        json.dump({"last_verse": verse_name}, file, ensure_ascii=False, indent=4)

def load_progress():
    try:
        with open("user_progress.json", "r", encoding="utf-8") as file:
            return json.load(file).get("last_verse", None)
    except FileNotFoundError:
        return None

# Step 5: GUI Application
class AudioBibleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Audio Bible System")
        self.root.geometry("600x500")
        self.root.set_theme("arc")  # Default theme

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

        # Custom Fonts
        self.title_font = ("Helvetica", 18, "bold")
        self.label_font = ("Helvetica", 12)
        self.button_font = ("Helvetica", 12, "bold")

        # Load Icons
        self.play_icon = self.load_icon("icons/play.png")
        self.pause_icon = self.load_icon("icons/pause.png")
        self.stop_icon = self.load_icon("icons/stop.png")
        self.loop_icon = self.load_icon("icons/loop.png")
        self.shuffle_icon = self.load_icon("icons/shuffle.png")

        # Dark Mode Toggle
        self.dark_mode = tk.BooleanVar(value=False)
        self.dark_mode_button = ttk.Checkbutton(root, text="Dark Mode", variable=self.dark_mode, command=self.toggle_dark_mode)
        self.dark_mode_button.pack(pady=10)

        # GUI Components
        self.title_label = ttk.Label(root, text="Enhanced Audio Bible System", font=self.title_font)
        self.title_label.pack(pady=20)

        self.verse_label = ttk.Label(root, text="Select a Verse:", font=self.label_font)
        self.verse_label.pack()

        # Dropdown for verse selection
        self.verse_var = tk.StringVar()
        self.verse_dropdown = ttk.Combobox(root, textvariable=self.verse_var, font=self.label_font)
        self.verse_dropdown["values"] = list(self.bible_data.keys())
        self.verse_dropdown.pack(pady=10)

        # Playback Controls Frame
        self.controls_frame = ttk.Frame(root)
        self.controls_frame.pack(pady=20)

        # Play Button
        self.play_button = ttk.Button(self.controls_frame, image=self.play_icon, command=self.play_verse)
        self.play_button.grid(row=0, column=0, padx=5)

        # Pause Button
        self.pause_button = ttk.Button(self.controls_frame, image=self.pause_icon, command=self.pause_audio)
        self.pause_button.grid(row=0, column=1, padx=5)

        # Stop Button
        self.stop_button = ttk.Button(self.controls_frame, image=self.stop_icon, command=self.stop_audio)
        self.stop_button.grid(row=0, column=2, padx=5)

        # Loop Button
        self.loop_button = ttk.Button(self.controls_frame, image=self.loop_icon, command=self.toggle_loop)
        self.loop_button.grid(row=0, column=3, padx=5)

        # Shuffle Button
        self.shuffle_button = ttk.Button(self.controls_frame, image=self.shuffle_icon, command=self.toggle_shuffle)
        self.shuffle_button.grid(row=0, column=4, padx=5)

        # Progress Label
        self.progress_label = ttk.Label(root, text="", font=self.label_font)
        self.progress_label.pack(pady=10)

        # Exit Button
        self.exit_button = ttk.Button(root, text="Exit", command=root.quit)
        self.exit_button.pack(pady=10)

        # Playback State
        self.is_playing = False
        self.is_paused = False
        self.is_looping = False
        self.is_shuffled = False

    def load_icon(self, path):
        """Load an icon image from the specified path."""
        image = Image.open(path)
        image = image.resize((32, 32), Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)

    def toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        if self.dark_mode.get():
            self.root.set_theme("equilux")  # Dark theme
        else:
            self.root.set_theme("arc")  # Light theme

    def play_verse(self):
        """Play the selected verse."""
        verse_name = self.verse_var.get()
        if verse_name in self.bible_data:
            audio_file = self.bible_data[verse_name]["audio_file"]
            text = self.bible_data[verse_name]["text"]
            self.progress_label.config(text=f"Playing {verse_name}: {text}")
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            save_progress(verse_name)  # Save progress
        else:
            self.progress_label.config(text=f"Verse {verse_name} not found.")

    def pause_audio(self):
        """Pause or resume the audio playback."""
        if self.is_playing:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            else:
                pygame.mixer.music.pause()
                self.is_paused = True

    def stop_audio(self):
        """Stop the audio playback."""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False

    def toggle_loop(self):
        """Toggle loop mode."""
        self.is_looping = not self.is_looping
        pygame.mixer.music.set_endevent(pygame.USEREVENT if self.is_looping else 0)

    def toggle_shuffle(self):
        """Toggle shuffle mode."""
        self.is_shuffled = not self.is_shuffled
        if self.is_shuffled:
            import random
            random.shuffle(list(self.bible_data.keys()))
        else:
            self.verse_dropdown["values"] = list(self.bible_data.keys())

# Run the application
if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # Use a modern theme
    app = AudioBibleApp(root)
    root.mainloop()