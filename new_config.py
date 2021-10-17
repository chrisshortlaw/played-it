#!python3

import os
if os.path.exists('env.py'):
    import env

class Config(object):

    IP = os.environ.get("IP")
    PORT = os.environ.get("PORT")
    SECRET_KEY = os.environ.get("SECRET_KEY") 
    MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
    MONGO_URI = os.environ.get("MONGO_URI") 
