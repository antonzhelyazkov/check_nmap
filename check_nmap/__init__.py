from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os
import logging


app = Flask(__name__)
db_mysql = SQLAlchemy()
verbose = (os.getenv('DEBUG', 'False') == 'True')

def create_app():
    load_dotenv()
    if verbose is True:
        logging.basicConfig(filename=os.getenv('LOG_FILE'), level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
    else:
        logging.basicConfig(filename=os.getenv('LOG_FILE'), level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASS')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db_mysql.init_app(app)

    from .procs import procs
    app.register_blueprint(procs, url_prefix='/')

    return app