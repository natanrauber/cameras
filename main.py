import tkinter as tk
from ctypes import byref, c_int, sizeof, windll
from tkinter import Canvas

import cv2
import numpy as np
from PIL import Image, ImageTk

exitFlag = False

def open_stream(url):
    return cv2.VideoCapture(url)

def restart_stream(cap, url):
    cap.release()
    return open_stream(url)

# List of stream URLs
stream_urls = [
    "rtsp://externa1218:Senha*1234@192.168.100.31:554/stream1",
    "rtsp://interna1218:Senha*1234@192.168.100.21:554/stream1",
    # Add more stream URLs as needed
]

# Create a list of captures
caps = [open_stream(url) for url in stream_urls]

# Initialize Tkinter
root = tk.Tk()
root.title("Cameras")
root.iconbitmap("icon.ico")
root.configure(bg='black')

def on_quit():
    global exitFlag
    exitFlag = True

root.protocol("WM_DELETE_WINDOW", on_quit)

HWND = windll.user32.GetParent(root.winfo_id())
windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(0x00800080)), sizeof(c_int))
windll.dwmapi.DwmSetWindowAttribute(HWND, 36, byref(c_int(0x00FFFFFF)), sizeof(c_int))
windll.dwmapi.DwmSetWindowAttribute(HWND, 34, byref(c_int(0x00FF00FF)), sizeof(c_int))

# Set the desired width and height for displaying frames
display_width = 960
display_height = 1000

# Create a Canvas widget to display frames
canvas = Canvas(root, width=display_width, height=display_height, bd=0, highlightthickness=0)
canvas.pack()

while exitFlag == False:
    frames = []
    rets = []

    for cap in caps:
        ret, frame = cap.read()
        rets.append(ret)
        frames.append(frame)

    for i, ret in enumerate(rets):
        if not ret:
            print(f"Error reading frame from stream {i + 1}. Restarting the stream...")
            caps[i] = restart_stream(caps[i], stream_urls[i])

    # Check if all streams are working
    if all(rets):
        # Concatenate frames vertically
        combined_frame = np.vstack(frames)

        # Resize the frame to fit within the specified width and height
        resized_frame = cv2.resize(combined_frame, (display_width, display_height))

        # Convert the frame to RGB format for displaying in Tkinter
        img_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        # Update the Canvas with the new image
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        root.update()

# Release all captures
for cap in caps:
    cap.release()

cv2.destroyAllWindows()
root.destroy()
