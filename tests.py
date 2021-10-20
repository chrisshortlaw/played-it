import unittest
from app import app, mongo
from app.models import User, Game, Review, Publisher
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
    
    def test_class_to_mongo(self):
        new_user = User.add_user(password='pass', name='test_user1', email='test@testuser.com', db_loc=mongo.db.tests)
        get_mongo_data = mongo.db.tests.find_one({"name":"test_user1"})
        check_dict = User.from_mongo(**get_mongo_data)
        self.assertTrue(check_dict._id is not None)
        self.assertEqual(check_dict._id, new_user._id)

        
        fake_pub = Publisher.create_publisher("Nintendo")
        fake_pub.upload_publisher(db_loc=mongo.db.tests)
        new_game = Game.add_game(label='fake game 4', platform='SNES', year=1996, genre='Sports', publisher=fake_pub, db_loc= mongo.db.tests)
        check_game_dict = Game.from_mongo(**(mongo.db.tests.find_one({"label": "fake game 4"})))
        self.assertTrue(check_game_dict._id is not None)
        self.assertEqual(check_game_dict._id, new_game._id)


    def test_class_from_mongo(self):
        new_user = User.add_user(password="pass", name="test_user1", email="test@testmail.com", db_loc=mongo.db.tests)

        fake_publisher = Publisher.create_publisher("Nintendo")
        fake_publisher.upload_publisher(db_loc=mongo.db.tests)
        new_game = Game.add_game("tekken", 'PlayStation', year=1997, genre='fighting', publisher=fake_publisher, db_loc=mongo.db.tests)       
        new_review = Review.add_review(name='Good', game=new_game.name, game_id=new_game._id, author=new_user.name, author_id=new_game._id, text="Okay", pub_date='12-12-21', db_loc=mongo.db.tests)

        self.assertTrue(new_user._id is not None)
        self.assertTrue(new_game._id is not None)
        self.assertTrue(new_review._id is not None)

        retrieve_user = mongo.db.tests.find_one({"_id": ObjectId(new_user._id)})
        retrieve_game = mongo.db.tests.find_one({"_id": ObjectId(new_game._id)})
        retrieve_review = mongo.db.tests.find_one({ "_id": ObjectId(new_review._id) })

        self.assertFalse(retrieve_user is None)
        self.assertFalse(retrieve_game is None)
        self.assertFalse(retrieve_review is None)

        game_from_mongo = Game.from_mongo(**retrieve_game)
        user_from_mongo = User.from_mongo(**retrieve_user)
        review_from_mongo = Review.from_mongo(**retrieve_review)

        self.assertEqual(game_from_mongo._id, new_game._id)
        self.assertEqual(review_from_mongo._id, new_review._id)
        self.assertEqual(user_from_mongo._id, new_user._id)
        fake_mongo_dict = {"_password": "pass", "name": "test_user3", "email": "test@usermail.com", "game_list": [], "reviews": [], "avatar_url": "this is a url"}

        #self.failUnlessRaises(exception=ValueError, callable=User.from_mongo(**fake_mongo_dict))

    def test_password(self):
        new_user = User.create_user(password="pass", name="test_user", email="test@user.com")
        self.assertTrue(new_user.check_pass('pass'))
        self.assertFalse(new_user.check_pass('dog'))


    def test_make_user(self):
        new_user = User.create_user(password="pass", name="test_user", email="test@user.com")
        added_user = mongo.db.tests.insert_one(new_user.__dict__)
        retrieve_user = mongo.db.tests.find_one({"name": "test_user"})
        self.assertEqual(added_user.inserted_id, retrieve_user["_id"])

    def test_add_user(self):
        new_user = User.add_user(password="password", name="new_user1", email="fake@fakemail.com", db_loc=mongo.db.tests)
        check_user = mongo.db.tests.find_one({"_id": ObjectId(new_user._id)} )
        self.assertEqual(check_user.get("_id"), new_user._id)

    def test_load_existing_user(self):
        new_user = User.create_user(password="pass", name="new_user2", email="fake2@fakemail.com")
        upload_id = new_user.upload_user(mongo.db.tests)
        retrieve_user = mongo.db.tests.find_one({"name": "new_user2"})
        self.assertEqual(upload_id._id, retrieve_user["_id"])

        self.assertFalse(upload_id._id != retrieve_user["_id"])

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
        pub_doc = Publisher.from_mongo(**mongo.db.publisher.find_one({"name": "nintendo"}))
        self.assertEqual(mongo.db.tests.find_one({"name": "fake_game"}), None)
        
        new_game = Game.add_game(
                label='fake_game', 
                platform='PlayStation', 
                year=1998, 
                genre='Sports', 
                publisher=pub_doc, 
                db_loc=mongo.db.tests
                )
        retrieved_game = mongo.db.tests.find_one({"_id": new_game._id})
        self.assertEqual(retrieved_game.get("publisher_id"), pub_doc._id)
        pub_doc2 = mongo.db.publisher.find_one({"name": "nintendo"})
        new_game2 = Game.add_game(
                        label='fake game 3', 
                        platform="SNES", 
                        year=1996, 
                        genre="action", 
                        publisher=pub_doc2, 
                        db_loc = mongo.db.tests
                        )
        retrieve_game_2 = mongo.db.tests.find_one({"label": "fake game 3"})
        self.assertEqual(retrieve_game_2.get("name"), new_game2.name)



    def test_game_retrieval(self):
        pass

    def test_add_review(self):
        pub_doc = mongo.db.publisher.find_one({"label": "Nintendo"}) 

        reviewed_game = mongo.db.tests.find_one({"label": "fake game 3"})
        if reviewed_game is None:
            new_game = Game.create_game(label='fake game 3', platform="SNES", year=1996, genre="action", publisher=pub_doc.get("label"), publisher_id=pub_doc.get('_id'))
            mongo.db.tests.insert_one(new_game.__dict__)
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


    def test_update_review(self):
        """
        Test the update function of the update review.
        """
        get_publisher = mongo.db.publisher.find_one({"label": "Nintendo"})
        new_user = User.add_user(password='pass', name='test_user1', email='test1@testmail.com', db_loc=mongo.db.tests)
        new_game = Game.add_game(label="fake_game3", platform='Wii', year=2003, genre='action', publisher=get_publisher, db_loc=mongo.db.tests)
        new_review = Review.add_review(
                name="I like this", game="fake game 3", game_id=new_game._id, 
                author=new_user.name, author_id = new_user._id, 
                text="This is good", pub_date="12-1-21", db_loc=mongo.db.tests
                )

        self.assertTrue(new_review._id is not None, 'Test')
        # store the id in a variable so it can be compared later
        review_id_check = new_review._id
        self.assertEqual(review_id_check, new_review._id)

        upload_check = Review.from_mongo(**mongo.db.tests.find_one({"_id": ObjectId(review_id_check)}))
        self.assertTrue(upload_check._id is not None)
        self.assertEqual(upload_check._id, review_id_check)

        self.assertEqual(new_review.text, "This is good")
        new_review.name = "I dislike this"
        new_review.text = "This was not good"
        new_review.update_review(db_loc=mongo.db.tests)
        self.assertEqual(new_review.name, "I dislike this")
        self.assertEqual(new_review.text, "This was not good")
        self.assertEqual(new_review.id, review_id_check, 'Updt review and original ids should match. They do not.')

        retrieved_review = list(mongo.db.tests.find({"name": "I dislike this"})) 
        self.assertEqual(len(retrieved_review), 1)
        self.assertTrue(retrieved_review[0] is not None)

        retrieved_review = Review.from_mongo(**retrieved_review[0])
        self.assertEqual(retrieved_review._id, new_review._id)


    def test_update_user(self):
        new_user = User.add_user(password='pass', name='test_user1', email='test1@testmail.com', db_loc=mongo.db.tests)

        check_upload = mongo.db.tests.find_one({"name": "test_user1"})
        self.assertEqual(new_user._id, check_upload["_id"])
        
        new_user.update_user_with_dict(mongo.db.tests, **{"name": "mike_1", "email": "mike1@email.com"})

        self.assertEqual(new_user.name, 'mike_1')
        self.assertEqual(new_user.email, "mike1@email.com")
        
        check_upload = mongo.db.tests.find_one({ "name": "mike_1" })

        self.assertEqual(new_user._id, check_upload["_id"])


    def test_user_delete(self):

        new_user = User.add_user("pass", "test_user2", "user@usermail.com", mongo.db.tests)
        check_upload = mongo.db.tests.find_one({"_id": new_user._id})
        self.assertTrue(check_upload is not None)

        new_user.delete_user(mongo.db.tests)
        check_upload = mongo.db.tests.find_one({"_id": new_user._id})
        self.assertTrue(check_upload is None)


if __name__ == "__main__":
    unittest.main(verbosity=2)

