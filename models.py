#!Python3
import os
from terminusdb_client import WOQLClient
from terminusdb_client import WOQLSchema, DocumentTemplate, LexicalKey
from typing import Set
if os.path.exists("env.py"):
    import env
user = 'chris'
team = 'team_of_me'
endpoint = f"https://cloud.terminusdb.com/{team}/"
client = WOQLClient(endpoint)

schema = WOQLSchema()

class User(DocumentTemplate):
    """
    Class of user.
    TODO: Add login, password(hashed), etc.
    """
    _schema = schema
    _key = LexicalKey(['name'])
    name : str
    email : str
    played_games: Set['Game']


class Game(DocumentTemplate):
    """
    Document for Computer and video games
    fields with types:
    name -> str
    platform -> str
    rank -> int
    year -> int
    genre -> str
    publisher -> set(Publisher)
    na_sales -> float
    eu_sales -> float
    jp_sales -> float
    other_sales -> float
    global_sales -> float
    """
    _schema = schema
    _key = LexicalKey(['name', 'platform'])
    name: str
    label: str
    platform: str
    rank: int
    year: int
    genre: str
    publisher: Set['Publisher'] 
    na_sales: float
    eu_sales: float
    jp_sales: float
    other_sales: float
    global_sales: float


class Publisher(DocumentTemplate):
    _schema = schema
    _key = LexicalKey(['name'])
    label: str
    name: str

if __name__ == "__main__":
    client.connect(user=user, team=team, db="played_it_db", use_token=True) 
    schema.commit(client, commit_msg="Changed publisher schema. Added 'key_name'. ")

