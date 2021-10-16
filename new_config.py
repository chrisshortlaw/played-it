#!python3

import os
if os.path.exists('env.py'):
    import env

class Config(object):

    IP = os.environ.get("IP") or "0.0.0.0"

    PORT = os.environ.get("PORT") or "5000"

    SECRET_KEY = os.environ.get("SECRET_KEY") or 'Latticed!Multitask!Sullen!Marital!Matchbox!Dedicate!Saucy!Overlying'

    MONGO_DBNAME = os.environ.get("MONGO_DBNAME") #or "played_it_db"

    MONGO_URI = os.environ.get("MONGO_URI") 
