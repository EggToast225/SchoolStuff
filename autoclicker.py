# importing time and threading
import time
import threading # multiple threads of executions within a python program
from pynput.mouse import Button, Controller

#pynput.keyboard is used to watch events of keyboard for start and stop of auto-clicker

from pynput.keyboard import Listener, KeyCode

#control for autoclicker
delay = 0.0001
button = Button.left
start_stop_key = KeyCode(char = 'a')
stop_key = KeyCode(char='b')

class ClickMouse(threading.Thread):
    # delay and button is passed in class
    # to check execution of auto-clicker
    def __init__(self, delay, button):
        super(ClickMouse,self).__init__() # passes clickmouse to theading parent class
        self.delay = delay
        self.button = button
        self.running = False
        self.program_running = True

    def start_clicking(self): # turns on clicking
        self.running = True
        print("Auto-clicking starting")

    def stop_clicking(self): # turns off clicking
        self.running = False
        print("Auto-clicker stopping")
    
    def exit(self):          # exits program
        print("Exiting program.")
        self.stop_clicking()
        self.program_running = False

    def run(self):
        while self.program_running:
            while self.running:
                mouse.click(self.button)
                time.sleep(self.delay)
            time.sleep(0.1)



mouse = Controller() # create mouse controller instance
click_thread = ClickMouse(delay,button) # create auto clicker instance
click_thread.start() # start threading process

def on_press(key):
    if key == start_stop_key: # if the key is start_stop_key,
        if click_thread.running: 
            click_thread.stop_clicking()  # if it's running, stop clicking
        else: 
            click_thread.start_clicking() # start clicking iif 


    elif key == stop_key: # if it's the stop_key (exit program)
        click_thread.exit() # set program_running as false and stop clicking
        listener.stop()
    

with Listener(on_press=on_press) as listener:
    listener.join() # listens to key press
    

    


