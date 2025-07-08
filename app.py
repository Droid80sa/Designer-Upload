import os
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Allowed extensions and file size limit
ALLOWED_EXTENSIONS = {
    '.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif',
    '.zip', '.svg', '.eps', '.ai', '.psd', '.tif', '.tiff'
}
# 100MB per file
MAX_FILE_SIZE = 100 * 1024 * 1024
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename: str) -> bool:
    """Check if the filename has an allowed extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS

mail = Mail(app)

# Load designers list
with open('designers.json') as f:
    DESIGNERS = json.load(f)

@app.route('/')
def index():
    return render_template(
        'upload.html',
        designers=DESIGNERS
    )

@app.route('/upload', methods=['POST'])
def upload_files():
    data = request.form
    designer_name = data.get('designer')
    client_name = data.get('client_name')
    client_email = data.get('email')
    contact = data.get('contact')
    instructions = data.get('instructions')

    # Find designer email
    designer_email = next(
        (d["email"] for d in DESIGNERS if d["name"] == designer_name),
        "production@hotink.co.za"
    )

    uploaded_files = []  # list of saved unique filenames
    original_files = []  # keep originals for reference if needed
    files = request.files.getlist('file')

    for file in files:
        if file.filename != "":
            if not allowed_file(file.filename):
                return jsonify({"error": "invalid file type"}), 400

            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)
            if size > MAX_FILE_SIZE:
                return jsonify({"error": "file too large"}), 400

            original_name = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{original_name}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            file.save(save_path)
            uploaded_files.append(unique_name)
            original_files.append(original_name)

    # Log upload
    log_upload(
        designer_name,
        client_name,
        client_email,
        contact,
        instructions,
        uploaded_files
    )

    # Send email
    send_notification(
        designer_email,
        client_name,
        client_email,
        contact,
        instructions,
        uploaded_files
    )

    return jsonify({"message": "success"})

def log_upload(designer, name, email, contact, instructions, files):
    log_file = app.config['CSV_LOG']
    row = {
        'Date': datetime.now().isoformat(),
        'Designer': designer,
        'Client Name': name,
        'Email': email,
        'Contact': contact,
        'Instructions': instructions,
        'Files': ", ".join(files)
    }

    if not os.path.exists(log_file):
        df = pd.DataFrame([row])
        df.to_csv(log_file, index=False)
    else:
        df = pd.read_csv(log_file)
        df = pd.concat([df, pd.DataFrame([row])])
        df.to_csv(log_file, index=False)

def send_notification(designer_email, name, email, contact, instructions, files):
    msg = Message(
        subject=f"New Artwork Upload from {name}",
        recipients=[designer_email]
    )
    body = f"""
New artwork uploaded:

Client Name: {name}
Email: {email}
Contact: {contact}
Instructions: {instructions}

Files:
{chr(10).join(files)}

Location on server:
/mnt/nas_uploads
"""
    msg.body = body
    mail.send(msg)
