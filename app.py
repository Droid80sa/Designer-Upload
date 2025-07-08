import os
import json
import csv
import fcntl
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

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
    """Append an upload entry to the CSV log with file locking."""
    log_file = app.config['CSV_LOG']
    row = {
        "Date": datetime.now().isoformat(),
        "Designer": designer,
        "Client Name": name,
        "Email": email,
        "Contact": contact,
        "Instructions": instructions,
        "Files": ", ".join(files),
    }

    # Ensure the directory for the log exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Open the file for reading and appending. This allows us to check for an
    # existing header after obtaining an exclusive lock.
    with open(log_file, "a+", newline="") as csvfile:
        fcntl.flock(csvfile, fcntl.LOCK_EX)

        csvfile.seek(0)
        has_data = csvfile.readline() != ""
        csvfile.seek(0, os.SEEK_END)

        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "Date",
                "Designer",
                "Client Name",
                "Email",
                "Contact",
                "Instructions",
                "Files",
            ],
        )

        if not has_data:
            writer.writeheader()

        writer.writerow(row)
        csvfile.flush()
        fcntl.flock(csvfile, fcntl.LOCK_UN)

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
