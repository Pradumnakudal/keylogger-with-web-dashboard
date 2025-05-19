import subprocess
import sys

required = [
    "requests",
    "pynput",
    "Pillow",
    "sounddevice",
    "scipy",
    "pywin32",
    "win32clipboard"
]

for package in required:
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
