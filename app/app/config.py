""" development configuration."""

import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = b'0\xd2\x11=A\xe3\xd8?>\x92=$\x03?|dQW\x84\x1eqr\x1e\xbe'
SESSION_COOKIE_NAME = 'login'

# File Upload to var/uploads/
APP_ROOT = pathlib.Path(__file__).resolve().parent
UPLOAD_FOLDER = APP_ROOT / 'var' / 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Database file is var/app.sqlite3
DATABASE_FILENAME = APP_ROOT / 'var' / 'app.sqlite3'