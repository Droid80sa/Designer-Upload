import io
import pandas as pd

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

    # File saved
    assert (upload_folder / 'hello.txt').exists()

    # CSV log updated
    df = pd.read_csv(csv_log)
    assert df.iloc[0]['Client Name'] == 'Tester'
    assert df.iloc[0]['Files'] == 'hello.txt'

    # Email sent
    send_mock.assert_called_once()
    msg = send_mock.call_args.args[0]
    assert 'Tester' in msg.subject
    assert msg.recipients == ['andrew@hotink.co.za']
    assert 'hello.txt' in msg.body
