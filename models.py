#!Python3.9
from typing import TypeVar, Type, Set

from terminusdb_client import WOQLSchema, DocumentTemplate, LexicalKey, HashKey, RandomKey
from werkzeug.security import check_password_hash, generate_password_hash 

from database import played_it_db

Game = TypeVar('Game')
User = TypeVar('User')
Publisher = TypeVar('Publisher')
Review = TypeVar('Review')


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

    @classmethod
    def create_pass(cls, password: str) -> str:
        hashed_pass = generate_password_hash(password_string, method='pbkdf2:sha256', salt_length=16)
        return hashed_pass
        
    @classmethod
    def create_username(cls, username: str) -> str:
        pass
    
    @classmethod
    def create_user(cls: Type[User], password: str, name:str, email:str, played_games: set['Game'] = set(), reviews: set['Review'] = set()) -> User:
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
    title: str
    platform: str
    year: int
    genre: str
    publisher: Set['Publisher'] 

    @classmethod
    def create_name(cls: Type[Game], label: str) -> str:
        name = label.lowercase().replace(" ", "_")
        return name

    @classmethod
    def create_game(cls: Type[Game], title: str, platform: str, year: int, genre: str, publisher: Type[Publisher]) -> Game:
        name = cls.create_name(title)
        return cls(name=name, title=title, platform=platform, year=year, genre=genre, publisher=publisher)


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
    title: str
    name: str

    @classmethod
    def create_publisher(cls, title):
        name = str(title).replace(" ", "_").lower()
        return cls(title=title, name=name)


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
    schema.commit(played_it_db.client, commit_msg='Test Commit: Is this working?')

