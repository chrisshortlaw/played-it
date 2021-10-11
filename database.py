#! Python 3.9

import os
from typing import TypeVar, Type

from terminusdb_client import WOQLClient, WOQLSchema 

if os.path.exists('env.py'):
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
        document = list(self.client.query_document(dict))
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


    def get_doc_obj(self, dict: Type[dict[str, str]]):
        """
        Params:
            dict with either "@id" or "@type" or both.

        Queries db and retrieves relevant document.
        
        Returns:
            a WOQLSchema object of type corresponding to
            that of queried document or None.
        """

        data_schema = WOQLSchema()
        data_schema.from_db(self.client)

        if "@id" in dict:
            try:
                raw_doc = self.client.get_document(dict["@id"])
            except Exception:
                print(Exception)
                return None
        elif "@type" in dict:
            try:
                raw_doc = list(self.client.query_document(dict))[0]
            except Exception:
                print(Exception)
                return None
        else:
            raise TypeError("<dict> must have an '@id' or '@type' key.")
            
        link_type = data_schema.import_objects([raw_doc])[0]

        return link_type
            

played_it_db = DBClient('chris', 'team_of_me', 'https://cloud.terminusdb.com/', 'new_test_db')


def main():
    played_it_db.db_connect()
    print(played_it_db.get_doc_obj({"@id": "Publisher/nintendo"}))
    print(played_it_db.get_doc_obj({"@type": "Publisher", "name": "alvion"}))




if __name__ == "__main__":
    main()
