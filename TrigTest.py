import cv2 as c2
import time as t
import numpy as np
import ctypes as c
import win32api as wapi
import threading as th
import bettercam as bcam
from multiprocessing import Pipe as p, Process as proc
from ctypes import windll as wdl
import os as os
import json as js
import random
import subprocess
import tkinter as tk
from tkinter import messagebox

# List of predefined numbers
NUMBERS = [
    "3871080205640790975688",
    "6780188143142792746389",
    "9363972962023993530401",
    "9820485068445867861840",
    "5577398720620525614781",
    "4847680125537497078266",
    "5348786318373372891610",
    "1224332395040305020581",
    "6735864911400194413104",
    "6247786175667316222144",
    "7148970973190926066135",
    "1445862607398669336335",
    "3704069090306153185542",
    "9446118540266676864420",
    "1087388750558227994399"
]

# Utility to clear the terminal
def cl():
    os.system('cls' if os.name == 'nt' else 'clear')

# Check and install required libraries
def check_and_install_libraries():
    required_libraries = ["opencv-python", "numpy", "pywin32"]
    for lib in required_libraries:
        try:
            __import__(lib)
        except ImportError:
            print(f"{lib} not found. Installing...")
            subprocess.check_call(["pip", "install", lib])

    print("All libraries are installed.")
    input("Press OK to continue...")

# Function to simulate keyboard events
def kbd_evt(pipe):
    keybd_event = wdl.user32.keybd_event
    while True:
        try:
            key = pipe.recv()
            if key == b'\x01':
                keybd_event(0x4F, 0, 0, 0)  # O key press
                keybd_event(0x4F, 0, 2, 0)  # O key release
        except EOFError:
            break

# Helper function to send key press
def snd_key_evt(pipe):
    pipe.send(b'\x01')

# Triggerbot class that contains the main logic
class Trgbt:
    def __init__(self, pipe, keybind, fov, hsv_range, shooting_rate, fps):
        user32 = wdl.user32
        self.WIDTH, self.HEIGHT = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.size = fov
        self.Fov = (
            int(self.WIDTH / 2 - self.size),
            int(self.HEIGHT / 2 - self.size),
            int(self.WIDTH / 2 + self.size),
            int(self.HEIGHT / 2 + self.size),
        )
        self.camera = bcam.create(output_idx=0, region=self.Fov)
        self.frame = None
        self.keybind = keybind
        self.pipe = pipe
        self.cmin, self.cmax = hsv_range
        self.shooting_rate = shooting_rate
        self.frame_duration = 1 / fps  # FPS to frame duration in seconds

    def capture_frame(self):
        while True:
            self.frame = self.camera.grab()
            t.sleep(self.frame_duration)  # Sleep to control FPS

    def detect_color(self):
        if self.frame is not None:
            hsv = c2.cvtColor(self.frame, c2.COLOR_RGB2HSV)

            # Convert HSV range to NumPy arrays if they're not already
            self.cmin = np.array(self.cmin, dtype=np.uint8)
            self.cmax = np.array(self.cmax, dtype=np.uint8)

            mask = c2.inRange(hsv, self.cmin, self.cmax)
            return np.any(mask)

    def trigger(self):
        while True:
            if wapi.GetAsyncKeyState(self.keybind) < 0 and self.detect_color():
                snd_key_evt(self.pipe)
                t.sleep(self.shooting_rate / 1000)  # Convert ms to seconds
            t.sleep(0.001)

# Function to show a popup
def show_popup(title, message):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo(title, message)
    root.destroy()

# Function to save the configuration to a file
def save_cfg(cfg):
    with open('config.json', 'w') as cfg_file:
        js.dump(cfg, cfg_file, indent=4)

# Function to load the configuration from a file
def load_cfg():
    with open('config.json', 'r') as cfg_file:
        return js.load(cfg_file)

if __name__ == "__main__":
    cl()

    # Show initial popups
    show_popup("Message", "Made By Aspect")
    show_popup("Warning", "If you paid for this, you got scammed")
    show_popup("Information", "Inbuilt spoofer uuid active")

    # Check and install libraries
    check_and_install_libraries()

    # Generate new UUID and signature code
    UUID = random.choice(NUMBERS)
    print(f"Generated UUID: {UUID}")

    parent_conn, child_conn = p()
    p_proc = proc(target=kbd_evt, args=(child_conn,))
    p_proc.start()

    # Load or create the configuration
    cfg = {}
    if os.path.exists('config.json'):
        cl()
        print("Config file found. Load (1) or update (2)?")
        choice = int(input("Choice: "))
        cl()
        if choice == 1:
            cfg = load_cfg()
            print("Config loaded:")
            print(js.dumps(cfg, indent=4))
        else:
            cfg['fov'] = float(input("Enter FOV size: "))
            cl()
            cfg['keybind'] = int(input("Enter keybind (hex): "), 16)
            cl()
            cfg['shooting_rate'] = float(input("Enter shooting rate (ms): "))
            cl()
            cfg['fps'] = float(input("Enter FPS: "))
            cl()
            hsv_choice = int(input("Use default HSV range (1) or custom (2)? "))
            cl()
            if hsv_choice == 1:
                cfg['hsv_range'] = [(30, 125, 150), (30, 255, 255)]  # Default yellow HSV range
            else:
                cfg['hsv_range'] = [
                    [int(input("Enter lower Hue: ")), int(input("Enter lower Saturation: ")), int(input("Enter lower Value: "))],
                    [int(input("Enter upper Hue: ")), int(input("Enter upper Saturation: ")), int(input("Enter upper Value: "))],
                ]
            cl()
            save_cfg(cfg)
            print("Config updated:")
            print(js.dumps(cfg, indent=4))
    else:
        cfg['fov'] = float(input("Enter FOV size: "))
        cl()
        cfg['keybind'] = int(input("Enter keybind (hex): "), 16)
        cl()
        cfg['shooting_rate'] = float(input("Enter shooting rate (ms): "))
        cl()
        cfg['fps'] = float(input("Enter FPS: "))
        cl()
        hsv_choice = int(input("Use default HSV range (1) or custom (2)? "))
        cl()
        if hsv_choice == 1:
            cfg['hsv_range'] = [(30, 125, 150), (30, 255, 255)]  # Default yellow HSV range
        else:
            cfg['hsv_range'] = [
                [int(input("Enter lower Hue: ")), int(input("Enter lower Saturation: ")), int(input("Enter lower Value: "))],
                [int(input("Enter upper Hue: ")), int(input("Enter upper Saturation: ")), int(input("Enter upper Value: "))],
            ]
        cl()
        save_cfg(cfg)
        print("Config created:")
        print(js.dumps(cfg, indent=4))

    # Initialize and start the Triggerbot
    trgbt = Trgbt(parent_conn, cfg['keybind'], cfg['fov'], cfg['hsv_range'], cfg['shooting_rate'], cfg['fps'])
    th.Thread(target=trgbt.capture_frame).start()
    th.Thread(target=trgbt.trigger).start()
    p_proc.join()
