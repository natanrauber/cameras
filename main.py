import time
import tkinter as tk
from ctypes import byref, c_int, sizeof, windll
from tkinter import Canvas

import cv2
import numpy as np
from PIL import Image, ImageTk

import lib.config as cfg

exitFlag: bool = False
last_restart_time: float = time.time()


def open_stream(url: str) -> cv2.VideoCapture:
    return cv2.VideoCapture(url)


def restart_stream(cap: cv2.VideoCapture, url: str) -> cv2.VideoCapture:
    cap.release()
    time.sleep(1)
    return open_stream(url)


def restart_streams(_):
    print("Restarting streams...")
    global last_restart_time
    for i, cap in enumerate(caps):
        caps[i] = restart_stream(cap, cfg.stream_urls[i])
    last_restart_time = time.time()


# Release all captures
def on_quit() -> None:
    global exitFlag
    exitFlag = True
    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()
    root.destroy()


# Create a list of captures
caps: list[cv2.VideoCapture] = [open_stream(e) for e in cfg.stream_urls]


# Initialize Tkinter
root: tk.Tk = tk.Tk()
root.title("Cameras")
root.iconbitmap("icon.ico")
root.configure(bg="black")
root.attributes("-fullscreen", True)
root.protocol("WM_DELETE_WINDOW", on_quit)
root.bind("<F5>", restart_streams)


HWND = windll.user32.GetParent(root.winfo_id())
windll.dwmapi.DwmSetWindowAttribute(
    HWND,
    35,
    byref(c_int(0x00140E0C)),
    sizeof(c_int),
)
windll.dwmapi.DwmSetWindowAttribute(
    HWND,
    36,
    byref(c_int(0x00FFFFFF)),
    sizeof(c_int),
)
windll.dwmapi.DwmSetWindowAttribute(
    HWND,
    34,
    byref(c_int(0x00312C8D)),
    sizeof(c_int),
)


# Create a Canvas widget to display frames
canvas: Canvas = Canvas(
    root,
    width=cfg.display_width,
    height=cfg.display_height,
    bd=0,
    highlightthickness=0,
)
canvas.pack()


while not exitFlag:
    current_time = time.time()
    elapsed_time = current_time - last_restart_time

    # Check if it's time to restart the streams
    if elapsed_time >= cfg.restart_interval:
        restart_streams(None)

    frames = []
    rets = []

    for cap in caps:
        ret, frame = cap.read()
        rets.append(ret)
        frames.append(frame)

    for i, ret in enumerate(rets):
        if not ret:
            print(f"Error reading from stream {i + 1}. Restarting stream...")
            caps[i] = restart_stream(caps[i], cfg.stream_urls[i])

    # Check if all streams are working
    if all(rets):
        # Concatenate frames vertically
        combined_frame = np.vstack(frames)

        # Resize the frame to fit within the specified width and height
        resized_frame = cv2.resize(
            combined_frame,
            (cfg.display_width, cfg.display_height),
        )

        # Convert the frame to RGB format for displaying in Tkinter
        img_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        # Update the Canvas with the new image
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        root.update()
