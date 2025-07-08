import io
import pytest
from unittest.mock import MagicMock

from app import app, mail

@pytest.fixture
def app_client(tmp_path, monkeypatch):
    upload_folder = tmp_path / "uploads"
    upload_folder.mkdir()
    csv_log = tmp_path / "upload_log.csv"

    app.config['UPLOAD_FOLDER'] = str(upload_folder)
    app.config['CSV_LOG'] = str(csv_log)

    send_mock = MagicMock()
    monkeypatch.setattr(mail, "send", send_mock)

    with app.test_client() as client:
        yield client, send_mock, csv_log, upload_folder
