import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'somesecretkey')
    UPLOAD_FOLDER = '/mnt/nas_uploads'
    CSV_LOG = os.path.join(UPLOAD_FOLDER, 'upload_log.csv')

    MAIL_SERVER = 'smtp.hotink.co.za'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'proofs@hotink.co.za'
    MAIL_PASSWORD = '55l0ngstr33tCT'
    MAIL_DEFAULT_SENDER = 'proofs@hotink.co.za'
    PUBLIC_BASE_URL = 'https://upload.hotink.org.za'
