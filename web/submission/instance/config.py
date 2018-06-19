import os
basedir = os.path.abspath(os.path.dirname(__file__))

db_ip = os.environ.get("SUBMISSION_DB_PORT_5432_TCP_ADDR") # ip of the linked postgres container (<linked container name>_PORT_<num port>_<protocol>_ADDR)
db_port = os.environ.get("SUBMISSION_DB_PORT_5432_TCP_PORT") # port of the linked postgres container (<linked container name>_PORT_<num port>_<protocol>_ADDR)

DEBUG = True
WTF_CSRF_ENABLED = True
SECRET_KEY = 'somesecretkey'
SQLALCHEMY_DATABASE_URI = "postgresql://myuser:mypassword@{0}:{1}/submission_db".format(db_ip, db_port)
SQLALCHEMY_TRACK_MODIFICATIONS = False


# flask-security
SECURITY_REGISTERABLE = True
SECURITY_REGISTER_URL = '/signup'
SECURITY_PASSWORD_HASH = 'sha512_crypt'
SECURITY_PASSWORD_SALT = 'kfoddddlhjdkljshaf67t7$8lkk93'
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
#MAIL_SERVER = 'smtp.gmail.com'
#MAIL_PORT = 465
#MAIL_USE_SSL = True
#MAIL_USERNAME = 'gmailusername'
#MAIL_PASSWORD = 'gmailpassword'

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'files', 'upload')
GROUNDTRUTH_FOLDER = os.path.join(os.path.dirname(__file__), 'files', 'groundtruth')

