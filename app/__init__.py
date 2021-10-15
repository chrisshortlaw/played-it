import os
from config import Config
if os.path.exists("env.py"):
    import env

# init script here
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from app.database_mongo import mongo

from app import routes, errors
