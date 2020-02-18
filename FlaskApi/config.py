import os

from dotenv import load_dotenv, find_dotenv

#---------------FILE UPLOADS---------------------#

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads'.format(PROJECT_HOME)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#--------------------END--------------------------#

ENV_PATH = '{}/env/.env'.format(PROJECT_HOME)

load_dotenv(dotenv_path=ENV_PATH)

db_uri= os.getenv("DB_URI")
