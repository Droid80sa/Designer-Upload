import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'somesecretkey')
    UPLOAD_FOLDER = '/mnt/nas_uploads'
    CSV_LOG = os.path.join(UPLOAD_FOLDER, 'upload_log.csv')

    MAIL_SERVER = 'smtp.hotink.co.za'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'proofs@hotink.co.za')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
    PUBLIC_BASE_URL = 'https://upload.hotink.org.za'
