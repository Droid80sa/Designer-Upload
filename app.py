import os
import json
import csv
import fcntl
import re
import logging
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    flash,
    send_from_directory,
)
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

DESIGNER_IMAGES_FOLDER = app.config['DESIGNER_IMAGES_FOLDER']
CSS_FILE = app.config['CSS_FILE']
DEFAULT_AVATAR = os.path.basename(app.config['DEFAULT_AVATAR'])
DESIGNERS_JSON = app.config['DESIGNERS_JSON']

def load_designers():
    with open(DESIGNERS_JSON) as f:
        designers = json.load(f)
    for d in designers:
        d.setdefault('avatar', DEFAULT_AVATAR)
    return designers

def save_designers(designers):
    with open(DESIGNERS_JSON, 'w') as f:
        json.dump(designers, f, indent=2)

DESIGNERS = load_designers()

# Allowed extensions and file size limit
ALLOWED_EXTENSIONS = {
    '.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif',
    '.zip', '.svg', '.eps', '.ai', '.psd', '.tif', '.tiff'
}
# 1000MB per file
MAX_FILE_SIZE = 1024 * 1024 * 1024
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename: str) -> bool:
    """Check if the filename has an allowed extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS

mail = Mail(app)


@app.route('/designer_data/avatars/<path:filename>')
def designer_avatar(filename):
    return send_from_directory(DESIGNER_IMAGES_FOLDER, filename)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return fn(*args, **kwargs)
    return wrapper


def update_css_variable(variable: str, value: str) -> bool:
    """Update a CSS variable in the dashboard stylesheet."""
    pattern = re.compile(
        rf"(^\s*{re.escape(variable)}\s*:)\s*[^;]+(;)",
        re.MULTILINE,
    )
    with open(CSS_FILE) as f:
        content = f.read()
    new_content, count = pattern.subn(rf"\1 {value}\2", content, count=1)
    if count:
        with open(CSS_FILE, 'w') as f:
            f.write(new_content)
        return True
    return False

@app.route('/')
def index():
    return render_template(
        'upload.html',
        designers=DESIGNERS,
        default_avatar=DEFAULT_AVATAR
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
    files = request.files.getlist('file') or request.files.getlist('file[]')

    # Debug: log what files Flask received
    logging.info(f"Received files: {[f.filename for f in files]}")

    # Ensure upload folder exists before saving files
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    logging.info(f"request.files keys: {list(request.files.keys())}")
    logging.info(f"Form keys: {list(request.form.keys())}")
    logging.info(f"Files received:")
    for file in files:
        logging.info(f"Processing file: {file.filename}")
        if file.filename != "":
            if not allowed_file(file.filename):
                logging.warning(f"File '{file.filename}' rejected: invalid type.")
                return jsonify({"error": "invalid file type"}), 400

            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)

            if size > MAX_FILE_SIZE:
                logging.warning(f"File '{file.filename}' rejected: too large.")
                return jsonify({"error": "file too large"}), 400

            original_name = secure_filename(file.filename)
            designer_tag = (designer_name or "design")[:3].lower()
            short_uuid = uuid.uuid4().hex[:4]
            unique_name = f"{designer_tag}_{short_uuid}_{original_name}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            file.save(save_path)
            uploaded_files.append(unique_name)
            original_files.append(original_name)
            logging.info(f"Saved file as: {save_path}")

    logging.info(f"Files saved: {uploaded_files}")

    # Log upload
    log_upload(
        designer_name,
        client_name,
        client_email,
        contact,
        instructions,
        uploaded_files
    )

    # Send email (pass original_files for user clarity)
    send_notification(
        designer_email,
        client_name,
        client_email,
        contact,
        instructions,
        uploaded_files,
        original_files,
    )

    return jsonify({"message": "success"})

def log_upload(designer, name, email, contact, instructions, files):
    log_file = app.config['CSV_LOG']
    row = {
        "Date": datetime.now().isoformat(),
        "Designer": designer,
        "Client Name": name,
        "Email": email,
        "Contact": contact,
        "Instructions": instructions,
        "Files": "\n".join(f"– {name}" for name in files),
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

def send_notification(designer_email, client_name, client_email, contact, instructions, uploaded_files, original_files):
    msg = Message(
    subject=f"New Artwork Upload from {client_name}",
    recipients=[designer_email]
    )
    msg.reply_to = client_email
    
    file_list = "\n".join(f"– {name}" for name in uploaded_files) if uploaded_files else "No files uploaded."

    body = f"""
A new design upload has been submitted.

Client Name: {client_name}
Client Email: {client_email}
Contact: {contact}
Instructions: {instructions}

Files Uploaded:
{file_list}

Location on server: {os.environ.get('FILE_SERVER_PATH', 'NAS/_Temp Work/ClientFiles')}
"""
    msg.body = body
    mail.send(msg)
    logging.info(f"Email sent to: {designer_email}")


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        flash('Invalid password')
    return render_template('login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/admin')
@login_required
def admin():
    variables = {}
    with open(CSS_FILE) as f:
        for line in f:
            m = re.match(r"\s*(--[^:]+):\s*([^;]+);", line)
            if m:
                variables[m.group(1)] = m.group(2)

    log_entries = []
    log_file = app.config['CSV_LOG']
    if os.path.exists(log_file):
        with open(log_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            log_entries = list(reader)

    return render_template(
        'admin.html',
        designers=DESIGNERS,
        variables=variables,
        log_entries=log_entries,
    )


@app.route('/admin/avatar', methods=['POST'])
@login_required
def upload_avatar():
    name = request.form.get('designer')
    file = request.files.get('avatar')
    if not name or not file:
        flash('Invalid data')
        return redirect(url_for('admin'))
    filename = secure_filename(file.filename)
    os.makedirs(DESIGNER_IMAGES_FOLDER, exist_ok=True)
    save_path = os.path.join(DESIGNER_IMAGES_FOLDER, filename)
    file.save(save_path)
    for d in DESIGNERS:
        if d['name'] == name:
            d['avatar'] = filename
            break
    save_designers(DESIGNERS)
    return redirect(url_for('admin'))

@app.route('/upload-test', methods=['GET', 'POST'])
def upload_test():
    if request.method == 'POST':
        for f in request.files.values():
            print("Received file:", f.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
            f.save(save_path)
        return "Upload received"

    return '''
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file" multiple>
      <button type="submit">Test Upload</button>
    </form>
    '''
@app.route("/email-test")
def email_test():
    msg = Message("Test Subject", recipients=["your_email@example.com"])
    msg.body = "Test email from Flask app"
    mail.send(msg)
    return "Test email sent"

@app.route('/admin/theme', methods=['POST'])
@login_required
def update_theme():
    variable = request.form.get('variable')
    value = request.form.get('value')
    if variable and value and update_css_variable(variable, value):
        flash('Theme updated')
    else:
        flash('Failed to update theme')
    return redirect(url_for('admin'))
