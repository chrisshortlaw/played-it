#! Python 3.9

from flask_pymongo import PyMongo

from app import app


mongo = PyMongo(app)
