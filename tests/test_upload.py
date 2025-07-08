import io
import os
import csv
from flask import url_for
from app import app

def test_file_upload(app_client):
    client, send_mock, csv_log, upload_folder = app_client

    data = {
        'designer': 'Andrew',
        'client_name': 'Tester',
        'email': 'tester@example.com',
        'contact': '123456',
        'instructions': 'Just testing'
    }

    data['file'] = (io.BytesIO(b'hello'), 'hello.txt')

    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.get_json() == {'message': 'success'}

    # File saved with unique name
    files = list(upload_folder.iterdir())
    assert len(files) == 1
    saved_name = files[0].name
    assert saved_name.endswith('hello.txt')
    assert saved_name != 'hello.txt'

    # CSV log updated
    with open(csv_log, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
    assert rows[0]['Client Name'] == 'Tester'
    assert rows[0]['Files'] == saved_name

    # Email sent
    send_mock.assert_called_once()
    msg = send_mock.call_args.args[0]
    assert 'Tester' in msg.subject
    assert msg.recipients == ['andrew@hotink.co.za']
    assert 'hello.txt' in msg.body


def test_designer_avatars_in_template(app_client):
    client, _, _, _ = app_client
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode()
    with app.test_request_context():
        for d in app.DESIGNERS:
            avatar_url = url_for('designer_avatar', filename=d['avatar'])
            assert avatar_url in html


def test_notification_includes_file_server_path(app_client, monkeypatch):
    client, send_mock, _, upload_folder = app_client

    app.config['FILE_SERVER_PATH'] = '/srv/files'

    data = {
        'designer': 'Andrew',
        'client_name': 'Tester',
        'email': 'tester@example.com',
        'contact': '123',
        'instructions': 'test'
    }
    data['file'] = (io.BytesIO(b'data'), 'path.txt')

    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200

    saved_name = next(upload_folder.iterdir()).name
    expected_path = os.path.join('/srv/files', saved_name)
    msg = send_mock.call_args.args[0]
    assert expected_path in msg.body
