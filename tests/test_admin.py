import io
import json
from pathlib import Path
from app import app


def login(client):
    return client.post('/admin/login', data={'password': app.config['ADMIN_PASSWORD']}, follow_redirects=True)


def test_avatar_upload(app_client, tmp_path):
    client, _, _, _ = app_client
    login(client)

    data = {
        'designer': 'Andrew',
        'avatar': (io.BytesIO(b'avatar'), 'new.png')
    }
    resp = client.post('/admin/avatar', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert resp.status_code == 200

    saved = Path(app.config['DESIGNER_IMAGES_FOLDER']) / 'new.png'
    assert saved.exists()

    with open(app.config['DESIGNERS_JSON']) as f:
        designers = json.load(f)
    for d in designers:
        if d['name'] == 'Andrew':
            assert d['avatar'].endswith('new.png')
            break
    else:
        assert False, 'Designer not updated'


def test_theme_update(app_client):
    client, _, _, _ = app_client
    login(client)

    css_path = Path(app.config['CSS_FILE'])
    original = css_path.read_text()

    resp = client.post('/admin/theme', data={'variable': '--teal', 'value': '#000000'}, follow_redirects=True)
    assert resp.status_code == 200
    new_content = css_path.read_text()
    assert '#000000' in new_content
    assert original != new_content


def test_upload_log_display(app_client):
    client, _, csv_log, _ = app_client
    login(client)

    import csv
    with open(csv_log, 'w', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                'Date', 'Designer', 'Client Name', 'Email',
                'Contact', 'Instructions', 'Files'
            ],
        )
        writer.writeheader()
        writer.writerow({
            'Date': '2024-01-01',
            'Designer': 'Andrew',
            'Client Name': 'Tester',
            'Email': 't@example.com',
            'Contact': '123',
            'Instructions': 'hi',
            'Files': 'file1.txt',
        })

    resp = client.get('/admin')
    assert resp.status_code == 200
    html = resp.data.decode()
    assert 'file1.txt' in html
    assert 'Tester' in html
