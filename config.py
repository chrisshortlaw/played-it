#!python3

import os
from terminusdb_client import WOQLClient
if os.path.exists('env.py'):
    import env

class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Latticed!Multitask!Sullen!Marital!Matchbox!Dedicate!Saucy!Overlying'

    
    TEAM = "team_of_me"

    DATABASE_NAME = "played_it_db"

    DB_URI = f"https://cloud.terminusdb.com/team_of_me/"

# SAMPLE DB CONNECT CODE:
# client=WOQLClient(Config.DB_URI)
# client.connect(team=Config.TEAM, jwt_token=Config.TERMINUSDB_ACCESS_TOKEN, db=Config.DATABASE_NAME,)
# Try setting token in environment variables
