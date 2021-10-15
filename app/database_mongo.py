#! Python 3.9

import os
from typing import TypeVar, Type

from flask_pymongo import PyMongo

if os.path.exists('env.py'):
    import env

from app import app


mongo = PyMongo(app)


# class DBClient:
    # """
    # Class for database configuration
    # Also holds query methods
    # """

    # def __init__(self, user, team, uri, db):
        # self.user = user
        # self.team = team
        # self.uri = uri 
        # self.endpoint = f"{self.uri}{self.team}/"
        # self.client = WOQLClient(self.endpoint)
        # self.db = db

    # def db_connect(self):
        # pass

    # def check_document_exists(self, dict: Type[dict]) -> bool:
        # return False
        

    # def get_first_document(self, dict: Type[dict[str, str]]):
        # """
        # TODO: Ensure type hinting is complete for this
        # """
        # return None


    # def get_doc_obj(self, dict: Type[dict[str, str]]):
        # """
        # Params:
            # dict with either "@id" or "@type" or both.

        # Queries db and retrieves relevant document.
        
        # Returns:
            # a WOQLSchema object of type corresponding to
            # that of queried document or None.
        # """

        # pass           



# def main():




