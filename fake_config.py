import os

class Config(object):

    SECRET_KEY = os.environ.get("SECRET_KEY") or "a_fake_key"

    MONGO_URI = os.environ.get("MONGO_URI") or "a_fake_uri"

    MONGO_DBNAME = os.environ.get("MONGO_DBNAME") or "a_fake_dbname"
