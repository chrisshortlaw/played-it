#!Python3.9
from typing import Type, Set
import os

from terminusdb_client import WOQLSchema, DocumentTemplate, LexicalKey, HashKey, RandomKey
from werkzeug.security import check_password_hash, generate_password_hash 

from database import played_it_db
if os.path.exists('env.py'):
    import env



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
    _key = HashKey(['email', 'name'])
    name : str
    email : str
    _password: str
    played_games: Set['Game']
    reviews: Set['Review']
    
    @property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, password_string):
        """
        To be used by User to change password
        runs password_string through the generate_password_hash function
        sets the User password as the newly hashed & salted string
        """
        hashed_pass = generate_password_hash(password_string, method='pbkdf2:sha256', salt_length=16)
        self._password = hashed_pass

    def check_pass(self, password_string):
        """
        To be used for login verification
        Checks hashed pass against password_string and returns True if match, false otherwise
        """
        return check_password_hash(self.password(), password_string)

    @classmethod
    def create_pass(cls, password):
        """
        Uses werkzeug built in password hash to generate a hashed pass and return it
        """
        hashed_pass = generate_password_hash(password_string, method='pbkdf2:sha256', salt_length=16)
        return hashed_pass
        
  #  @classmethod
   # def create_username(cls, username):
    #    """Creates a valid username or converts an invalid type to a valid type"""
     #   pass
    
    @classmethod
    def create_user(cls, password, name, email, played_games = set(), reviews = set()):
       # if name == name:        # insert Regex here
        #    pass
        #else:             
        hashed_pass = create_pass(password)
        return cls(name=name, email=email, _password=hashed_pass, played_games=played_games, reviews=reviews)


class Game(DocumentTemplate):
    """
    Document for Computer and video games
    fields with types:
    NOTE: name is in snake_case
    name -> str
    NOTE: label is natural case
    label -> str
    platform -> str
    year -> int
    genre -> str
    publisher -> set(Publisher)
    reviews -> Set['review']
    """
    _schema = schema
    _key = LexicalKey(['name', 'platform'])
    name: str
    label: str
    platform: str
    year: int
    genre: str
    publisher: Set['Publisher']
    reviews: Set['Review']

    @classmethod
    def create_name(cls, label):
        name = label.lower().replace(" ", "_")
        return name

    @classmethod
    def create_game(cls, label, platform, year, genre, publisher, reviews=set()):
        name = cls.create_name(label)
        return cls(name=name, label=label, platform=platform, year=year, genre=genre, publisher=publisher, reviews=reviews)


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

    @classmethod
    def create_publisher(cls, label):
        name = str(label).replace(" ", "_").lower()
        return cls(label=label, name=name)



class Review(DocumentTemplate):
    """
    _key = HashKey(['title', 'author'])
    title: str
    author: str 
    text: str
    game: Set['Game']
    pub-date: str 

    """
    _schema = schema
    _key = HashKey(['title', 'author'])
    title: str
    game: Set['Game'] 
    author: Set['User'] 
    text: str
    pub_date: str


def main():
    played_it_db.db_connect()
    schema.commit(played_it_db.client, commit_msg="Updated Review, Publisher, User, Game")


if __name__ == "__main__":
    main()
