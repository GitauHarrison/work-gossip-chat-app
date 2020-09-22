import unittest
from app import app, db
from app.models import User, Post
from datetime import datetime, timedelta

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username = 'harry')
        u.set_password('harry')
        self.assertFalse(u.check_password('cat'))
        self.assertTrue(u.check_password('harry'))

    def test_avatar(self):
        u = User(username = 'harry', email = 'harry@gmail.com')
        self.assertEqual(u.avatar(36), (
            'https://www.gravatar.com/avatar/'
            '3500e0f331aee41e9e3bdbb5431a9b0d'
            '?d=identicon&s=36'
        ))

    def test_follow(self):
        u1 = User(username = 'harry', email = 'harry@gmail.com')
        u2 = User(username = 'gitau', email = 'gitau@gmail.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followed.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'gitau')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'harry')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # create users
        u1 = User(username = 'harry', email = 'harry@gmail.com')
        u2 = User(username = 'gitau', email = 'gitau@gmail.com')
        u3 = User(username = 'rahima', email = 'rahima@gmail.com')
        u4 = User(username = 'nassir', email = 'nassir@gmail.com')

        # create posts
        now = datetime.utcnow()
        p1 = Post(body = 'post from harry', author = u1, timestamp = now + timedelta(seconds = 1))
        p2 = Post(body = 'post from gitau', author = u2, timestamp = now + timedelta(seconds=4))
        p3 = Post(body = 'post from rahima', author = u3, timestamp = now + timedelta(seconds=3))
        p4 = Post(body = 'post from nassir', author = u4, timestamp = now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # set up the follows
        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)

        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)