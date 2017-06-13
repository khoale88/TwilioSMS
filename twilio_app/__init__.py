from flask import Flask
app = Flask(__name__)
TESTING = True
from controllers import *