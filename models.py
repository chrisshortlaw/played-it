#!Python3.9
from typing import Type, Set, Optional, List
import os

from terminusdb_client import WOQLSchema, DocumentTemplate, LexicalKey, HashKey, RandomKey, WOQLClient  
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
        _key = LexicalKey['email', 'name'] - this should be unique and work for lexical key
        name: Username chosen by User -> str
        email: User's email -> str
        _password: set with self.password
        Note: Below were removed but may return.
        game_list: Optional["GameList"] 
        reviews: Optional["ReviewList"] 
    """
    _schema = schema
    _key = HashKey(['email', 'name'])
    name : str
    email : str
    _password: str
    reviews: Optional["ReviewList"]
    game_list: Optional["GameList"]
    
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
    def create_pass(cls, password_string):
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
    def create_user(cls, password, name, email):
       # if name == name:        # insert Regex here
        #    pass
        #else:             
        hashed_pass = User.create_pass(password)
        return cls(name=name, email=email, _password=hashed_pass) 


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
    reviews: Optional['ReviewList']

    @classmethod
    def create_name(cls, label):
        name = label.lower().replace(" ", "_")
        return name

    @classmethod
    def create_game(cls, label, platform, year, genre, publisher):
        name = cls.create_name(label)
        return cls(name=name, label=label, platform=platform, year=year, genre=genre, publisher=publisher) 


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
    _key = HashKey(['title', 'author_name'])
    title: str
    game: Optional["Game"]      # GameDoc -> Ref for Game
    game_label: str             # label for game
    _game_id: str               # @id for game
    author: Optional["User"]    # AuthorDoc -> Ref for User
    author_name: str            # str -> name for user 
    _author: str                # @id for user
    text: str                   # Text of Review
    pub_date: str               # Publication Date of Review in str

    """
    _schema = schema
    _key = HashKey(['title', 'author_name', 'pub_date'])
    title: str
    game: Optional["Game"]      # GameDoc -> Ref for Game
    game_label: str             # label for game
    _game_id: str               # @id for game
    author: Optional["User"]    # AuthorDoc -> Ref for User
    author_name: str            # str -> name for user 
    _author: str                # @id for user
    text: str                   # Text of Review
    pub_date: str               # Publication Date of Review in str



class GameList(DocumentTemplate):
    """
    key: RandomKey
    user -> str @id "User"
    games: List["Game"]
    """
    _schema = schema
    _key = RandomKey()
    user: str 
    games: Set[str]


class ReviewList(DocumentTemplate):
    """
    key: RandomKey
    game -> str @id "Game"
    reviews -> List["Review"]
    """
    _schema = schema
    _key = RandomKey()
    game: str
    reviews: Set[str]


def main():
#   Update Schema
    played_it_db.db_connect()
    schema.commit(played_it_db.client, commit_msg="Updated ReviewLIst & GameList Model")


if __name__ == "__main__":
    main()
    
