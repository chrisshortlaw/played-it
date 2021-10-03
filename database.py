#! Python 3.9

import os
from typing import TypeVar, Type

from terminusdb_client import WOQLClient

if os.path.exists('env'):
    import env


class DBClient:
    """
    Class for database configuration
    Also holds query methods
    """

    def __init__(self, user, team, uri, db):
        self.user = user
        self.team = team
        self.uri = uri 
        self.endpoint = f"{self.uri}{self.team}/"
        self.client = WOQLClient(self.endpoint)
        self.db = db

    def db_connect(self):
        self.client.connect(user=self.user, team=self.team, db=self.db, use_token=True)

    def check_document_exists(self, dict: Type[dict]) -> bool:
        # TODO: Check if id is used  and write try...except to query by id
        document = list(self.connect.query_document(dict))
        if len(document) == 1:
            return True
        else:
            return False

    def get_first_document(self, dict: Type[dict[str, str]]):
        """
        TODO: Ensure type hinting is complete for this
        """
        documents = list(self.client.query_document(dict))
        if len(documents) >= 1:
            return documents[0]
        else:
            return None

played_it_db = DBClient('chris', 'team_of_me', 'https://cloud.terminusdb.com/', 'new_test_db')

