import unittest
from app import app
from app.models import User, Game, Review, Publisher
from dataclasses import asdict
from app.database_mongo import mongo

class TestUser(unittest.TestCase):

    def setUp(self):
        test_docs = mongo.db.tests.find({})
        if test_docs:
            mongo.db.tests.delete_many({})

    @classmethod
    def setUpClass(cls):
        test_docs = mongo.db.tests.find({})
        if test_docs:
            mongo.db.tests.delete_many({})
        else:
            pass
        
    @classmethod
    def tearDownClass(cls):
        mongo.db.tests.delete_many({})


    def test_password(self):
        new_user = User.create_user(password="pass", name="test_user", email="test@user.com")
        self.assertTrue(new_user.check_pass('pass'))
        self.assertFalse(new_user.check_pass('dog'))

    def test_add_user(self):
        new_user = User.create_user(password="pass", name="test_user", email="test@user.com")
        added_user = mongo.db.tests.insert_one(asdict(new_user))
        retrieve_user = mongo.db.tests.find_one({"name": "test_user"})
        self.assertEqual(added_user.inserted_id, retrieve_user["_id"])


    def test_add_game(self):
        pub_doc = mongo.db.publisher.find_one({"name": "nintendo"})
        new_game = Game.create_game(label='fake game 3', platform="SNES", year=1996, genre="action", publisher=pub_doc.get('_id'))
        self.assertEqual(mongo.db.tests.find_one({"name": new_game.name}), None)
        added_game = mongo.db.tests.insert_one(asdict(new_game))
        retrieved_game = mongo.db.tests.find_one({"_id": added_game.inserted_id})
        self.assertEqual(retrieved_game["publisher"], pub_doc["_id"])

    def test_game_retrieval(self):
        pass



    def test_add_review(self):
        pub_doc = mongo.db.publisher.find_one({"label": "Nintendo"}) 

        reviewed_game = mongo.db.tests.find_one({"label": "fake game 3"})
        if reviewed_game is None:
            new_game = Game.create_game(label='fake game 3', platform="SNES", year=1996, genre="action", publisher=pub_doc.get('_id'))
            mongo.db.tests.insert_one(asdict(new_game))
            reviewed_game = mongo.db.tests.find_one({"label": "fake game 3"})

        self.assertFalse(reviewed_game == None, 'Reviewed_game is not present in db')

        review_author = mongo.db.tests.find_one({"name": "test_user"})
        if review_author is None:
            new_user = User.create_user(password="pass", name="test_user", email="test@user.com")
            added_user = mongo.db.tests.insert_one(asdict(new_user))
            review_author = mongo.db.tests.find_one({ "name": "test_user" })

        self.assertFalse(review_author == None, 'User is not present in db')

        test_review = Review(title="Test Review", game=reviewed_game.get("_id"), game_label=reviewed_game.get("label"), author=review_author.get("_id"), author_name=review_author.get('name'), text="This is a test", pub_date="12-12-21")
        added_review = mongo.db.tests.insert_one(asdict(test_review))
        retrieved_review = mongo.db.tests.find_one({"title": test_review.title})
        self.assertEqual(added_review.inserted_id, retrieved_review["_id"])
        self.assertEqual(retrieved_review.get("game"), reviewed_game.get("_id"))
        self.assertEqual(retrieved_review.get("author"), review_author.get("_id"))
        

if __name__ == "__main__":
    unittest.main(verbosity=2)

