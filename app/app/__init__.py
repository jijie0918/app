from flask import Flask

app = Flask(__name__)
app.config.from_object('app.config')

from app import models
from app import api
from app import views
