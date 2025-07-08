import os
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from datetime import datetime
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

    uploaded_files = []
    files = request.files.getlist('file')

    for file in files:
        if file.filename != "":
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            uploaded_files.append(filename)

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
