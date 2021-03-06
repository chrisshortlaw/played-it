import os
from new_config import Config

# init script here
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)

from app.database_mongo import mongo

from app import routes, errors

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), port=os.environ.get("PORT")) #Note: removed process.env.PORT
