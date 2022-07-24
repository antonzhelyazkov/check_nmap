from flask import Flask
from dotenv import load_dotenv
import os
import logging

app = Flask(__name__)
verbose = (os.getenv('DEBUG', 'False') == 'True')

def create_app():
    load_dotenv()
    if verbose is True:
        logging.basicConfig(filename=os.getenv('LOG_FILE'), level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
    else:
        logging.basicConfig(filename=os.getenv('LOG_FILE'), level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
