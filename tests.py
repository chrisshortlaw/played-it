import unittest
from app import app, mongo
from app.models import User, Game, Review, Publisher
from dataclasses import asdict
#from app.database_mongo import mongo
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

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

    def test_make_user(self):
        new_user = User.create_user(password="pass", name="test_user", email="test@user.com")
        added_user = mongo.db.tests.insert_one(asdict(new_user))
        retrieve_user = mongo.db.tests.find_one({"name": "test_user"})
        self.assertEqual(added_user.inserted_id, retrieve_user["_id"])

    def test_add_user(self):
        new_user = User.add_user(password="password", name="new_user1", email="fake@fakemail.com", db_loc=mongo.db.tests)
        check_user = mongo.db.tests.find_one({"_id": ObjectId(new_user)} )
        self.assertEqual(check_user["_id"], new_user)

    def test_load_existing_user(self):
        new_user = User.create_user(password="pass", name="new_user2", email="fake2@fakemail.com")
        upload_id = new_user.upload_user(mongo.db.tests)
        retrieve_user = mongo.db.tests.find_one({"name": "new_user2"})
        self.assertEqual(upload_id, retrieve_user["_id"])
        self.assertFalse(upload_id != retrieve_user["_id"])

    def test_check_user(self):
        new_user = User.add_user(password="pass", name="new_user2", email="fake2@fakemail.com", db_loc=mongo.db.tests)
        check_user = mongo.db.tests.find({"name": "new_user2"})
        self.assertTrue(len(list(check_user)) == 1)
        if check_user:
            pass
        else:
            another_user = User.add_user(password="pass", name="new_user2", email="fake@fakemail.com", db_loc=mongo.db.tests)
        check_duplicate = list(mongo.db.tests.find({"name": "new_user2"}))
        self.assertFalse(len(check_duplicate) > 1)


    def test_check_user_email(self):
        new_user = User.add_user(password="pass", name="new_user2", email="fake2@fakemail.com", db_loc=mongo.db.tests)
        check_user = mongo.db.tests.find({"email":"fake2@fakemail.com"})
        self.assertTrue(len(list(check_user)) == 1)
        if check_user:
            pass
        else:
            another_user = User.add_user(password="pass", name="new_user2", email="fake2@fakemail.com", db_loc=mongo.db.tests)
        check_duplicate = list(mongo.db.tests.find({ "email": "fake2@fakemail.com" }))
        self.assertTrue(len(check_duplicate) == 1, 'Check Duplicate: Fail - Multiple Users detected.')
        session = {}
        self.assertTrue(check_password_hash(check_duplicate[0]['_password'], 'pass'))
        session['username'] = check_duplicate[0]['name']
        session['_id'] = check_duplicate[0]['_id']
        print(f"Check_Dup: {check_duplicate[0]['_id']}, Session: { session['_id'] }")
        self.assertTrue(session["_id"] == check_duplicate[0]["_id"])


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
            added_user = mongo.db.tests.insert_one(new_user.to_mongo_dict())
            review_author = mongo.db.tests.find_one({ "name": "test_user" })

        self.assertFalse(review_author == None, 'User is not present in db')

        test_review = Review(name="Test Review", game=reviewed_game['label'], game_id=reviewed_game['_id'], author=review_author["name"], author_id=review_author["_id"], text="This is a test review", pub_date="15-12-1984")
        added_review = mongo.db.tests.insert_one(test_review.to_mongo_dict())
        retrieved_review = mongo.db.tests.find_one({"name": test_review.name})
        self.assertEqual(added_review.inserted_id, retrieved_review["_id"])
        self.assertEqual(retrieved_review.get("game_id"), reviewed_game.get("_id"))
        self.assertEqual(retrieved_review.get("author_id"), review_author.get("_id"))
        

if __name__ == "__main__":
    unittest.main(verbosity=2)

