import io
import os
import sys
import json
import pytest
from unittest.mock import MagicMock

# Ensure the project root is on the import path so that ``app`` can be
# imported when the tests are executed from arbitrary working
# directories.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, mail, load_designers

@pytest.fixture
def app_client(tmp_path, monkeypatch):
    upload_folder = tmp_path / "uploads"
    upload_folder.mkdir()
    csv_log = tmp_path / "upload_log.csv"

    designers_json = tmp_path / "designers.json"
    css_file = tmp_path / "dashboard.css"
    designers_folder = tmp_path / "designers"
    designers_folder.mkdir()

    with open(os.path.join(os.path.dirname(__file__), "..", "designers.json")) as f:
        data = json.load(f)
    with open(designers_json, "w") as f:
        json.dump(data, f)

    with open(os.path.join(os.path.dirname(__file__), "..", "static", "css", "dashboard.css")) as fsrc:
        css_file.write_text(fsrc.read())

    app.config['UPLOAD_FOLDER'] = str(upload_folder)
    app.config['CSV_LOG'] = str(csv_log)
    app.config['DESIGNERS_JSON'] = str(designers_json)
    app.config['CSS_FILE'] = str(css_file)
    app.config['DESIGNER_IMAGES_FOLDER'] = str(designers_folder)
    app.config['ADMIN_PASSWORD'] = 'secret'

    app.DESIGNERS = load_designers()

    send_mock = MagicMock()
    monkeypatch.setattr(mail, "send", send_mock)

    with app.test_client() as client:
        yield client, send_mock, csv_log, upload_folder
