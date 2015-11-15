# {{ ansible_managed }}

DEBUG = True
SECRET_KEY = open('{{ api_dev_secret_key_path }}', 'rb').read()
SQLALCHEMY_DATABASE_URI = 'postgres://radar:{{ db_password }}@{{ db_host }}/radar'
SESSION_TIMEOUT = 86400
BASE_URL = 'http://localhost/#'
SQLALCHEMY_TRACK_MODIFICATIONS = False
