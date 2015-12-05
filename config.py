from datetime import timedelta


APP_NAME = 'Nosferatu'
DEBUG = False
CSRF_ENABLED = True
REMEMBER_COOKIE_DURATION = timedelta(days=3)
SQLALCHEMY_TRACK_MODIFICATIONS = False
TESTING = False

# Flask-User Config
USER_APP_NAME = 'Nosferatu'
USER_ENABLE_CONFIRM_EMAIL = False
USER_ENABLE_EMAIL = True
USER_ENABLE_FORGOT_PASSWORD = False
USER_ENABLE_LOGIN_WITHOUT_CONFIRM = True
USER_ENABLE_CHANGE_USERNAME = False
USER_ENABLE_USERNAME = False
USER_SEND_PASSWORD_CHANGED_EMAIL = False
USER_SEND_REGISTERED_EMAIL = False
USER_SEND_USERNAME_CHANGED_EMAIL = False
