# Plays a mp3 clip when mouse clicks
import threading # came across an issue where clicking would cause a huge performance dip
import os


from playsound import playsound
from pynput.mouse import Listener as MouseListener, Button
from pynput.keyboard import Listener as KeyboardListener, Key

# Plays an audio file in file path location
class SoundPlayer:
    def __init__(self, sound_path):
        self.sound_path = sound_path

    def play_sound(self):
        playsound(self.sound_path, False)

# Handles mouse listener that listens to mouse inputs
class MouseHandler:
    def __init__(self, sound_player: SoundPlayer):
        self.sound_player = sound_player
        self.listener = None
        self.sound_thread = None # use a single thread 

    def on_click(self, x, y,  button, pressed):
        if pressed and button == Button.left: # If mouse input is left click
            if self.sound_thread is None or not self.sound_thread.is_alive(): # If there isn't a thread, or previous thread action is finished, start another thread action
                self.sound_thread = threading.Thread(target = self.sound_player.play_sound, daemon= True)  # Allows for listener to run in background, daemon stops when main program ends
                self.sound_thread.start() 
    
# Handles mouse listener that listens to keyboard inputs
class KeyboardHandler:
    def __init__(self, mouse_handler: MouseHandler):
        self.listener = None
        self.mouse_hander = mouse_handler

    def stop_audio_click(self,key):
        if key == Key.esc: # If key press is esc, then stop the audio click.
            print("Stopping Keyboard Listener")
            self.listener.stop()
            print("Stopping Mouse Listener")
            self.mouse_hander.listener.stop()
        

# Basically main

sound_path = os.path.join(os.path.dirname(__file__), 'vine-boom.wav')

sound_player = SoundPlayer(sound_path)

# Handles mouse and keyboard actions, like what to do when clicked or pressed
mouse_handler = MouseHandler(sound_player)
keyboard_handler = KeyboardHandler(mouse_handler)

def startListeners(mouse, keyboard): # Assign the listeners for the handlers and start them
    keyboard.listener = KeyboardListener(on_press= keyboard.stop_audio_click)
    keyboard.listener.start()


    mouse.listener = MouseListener(on_click=mouse.on_click)
    mouse.listener.start()
    mouse.listener.join()


startListeners(mouse_handler, keyboard_handler)