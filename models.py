#!Python3
import os
from terminusdb_client import WOQLClient
from terminusdb_client import WOQLSchema, DocumentTemplate, LexicalKey, HashKey, RandomKey
from typing import Set
from werkzeug.security import check_password_hash, generate_password_hash 
if os.path.exists("env.py"):
    import env


class DBClient:

    def __init__(self, user, team, uri, db):
        self.user = user
        self.team = team
        self.uri = uri 
        self.endpoint = f"{self.uri}{self.team}/"
        self.client = WOQLClient(self.endpoint)
        self.db = db

    def db_connect(self):
        self.client.connect(user=self.user, team=self.team, db=self.db, use_token=True)


played_it_db = DBClient('chris', 'team_of_me', 'https://cloud.terminusdb.com/', 'new_test_db')


schema = WOQLSchema()

class User(DocumentTemplate):
    """
    Class of user.
    TODO: Add ability to like reviews, follow other Users and be followed.
    Schema: 
        _key = LexicalKey['email'] - this should be unique and work for lexical key
        name: Username chosen by User
        _password: set with self.password
        played_games: A Set of Documents the User has played. Added by User either after registration (TODO) or via a page on app
        reviews: List of reviews written by User. Reviews related to games
    """
    _schema = schema
    _key = LexicalKey(['email'])
    name : str
    email : str
    _password: str
    played_games: Set['Game']
    reviews: Set['Review']
    
    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, password_string: str) -> None:
        """
        To be used by User to change password
        runs password_string through the generate_password_hash function
        sets the User password as the newly hashed & salted string
        """
        hashed_pass = generate_password_hash(password_string, method='pbkdf2:sha256', salt_length=16)
        self._password = hashed_pass

    def check_pass(self, password_string: str) -> bool:
        """
        To be used for login verification
        Checks hashed pass against password_string and returns True if match, false otherwise
        """
        return check_password_hash(self.password(), password_string)
    


class Game(DocumentTemplate):
    """
    Document for Computer and video games
    fields with types:
    NOTE: name is in snake_case
    name -> str
    NOTE: label is natural case
    label -> str
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
    """
    Class for Publisher Document
    Key is LexicalKey which is taken from 'name' field
    Fields: name: str, label: str
    name: should have the pattern: 'devolver_digital, sony_computer_entertainment' -> lowercase, snake_case
    label: Regular spelling.
    """
    _schema = schema
    _key = LexicalKey(['name'])
    label: str
    name: str


class Review(DocumentTemplate):
    """
    _key = HashKey(['title', 'author'])
    title: str
    author: Set['User']
    text: str
    pub-day: int
    pub-month: int
    pub-year: int
    pub-date: Set['pub-day', 'pub-month', 'pub-year']

    """
    _schema = schema
    _key = HashKey(['title', 'author'])
    title: str
    game: Set['Game']
    author: Set['User']
    text: str
    pub_date: int


if __name__ == "__main__":
    played_it_db.db_connect()
    schema.commit(played_it_db.client, commit_msg="Uptd User, + _password methods")

