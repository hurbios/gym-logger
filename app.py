from os import getenv
from flask import Flask

app = Flask(__name__)
app.secret_key = getenv('SECRET_KEY')

#pylint: disable=wrong-import-position, disable=unused-import
import routes
