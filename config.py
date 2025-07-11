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

    # Admin settings
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')
    DESIGNERS_JSON = os.environ.get(
        'DESIGNERS_JSON', os.path.join('designer_data', 'designers.json')
    )
    DESIGNER_IMAGES_FOLDER = os.environ.get(
        'DESIGNER_IMAGES_FOLDER', os.path.join('designer_data', 'avatars')
    )
    DEFAULT_AVATAR = os.environ.get(
        'DEFAULT_AVATAR', os.path.join('designer_data', 'avatars', 'default_avatar.png')
    )
    CSS_FILE = os.environ.get(
        'CSS_FILE', os.path.join('static', 'css', 'dashboard.css')
    )

    # Base path shown in notification emails for uploaded files
    FILE_SERVER_PATH = os.environ.get(
        'FILE_SERVER_PATH', 'NAS/_Temp Work/ClientFiles'
    )
