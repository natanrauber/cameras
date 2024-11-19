# Set the desired width and height for displaying frames
display_height: int = 1080
display_width: int = int((display_height * (16 / 9)) / 2)

restart_interval = 60 * 10  # reload time in seconds

# List of stream URLs
stream_urls: list[str] = [
    "rtsp://externa1218:Senha*1234@192.168.100.31:554/stream2",
    "rtsp://interna1218:Senha*1234@192.168.100.21:554/stream2",
    # Add more stream URLs as needed
]
