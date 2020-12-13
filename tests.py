# pylint: disable=no-member
from datetime import datetime, timedelta
import unittest
# from app import app, db
from app import create_app, db
from app.models import User, Post
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

# 사용자 모델 단위 테스트

class UserModelCase(unittest.TestCase):
    # setUp()에서 파일을 생성하고, tearDown()에서 파일을 삭제   -> Test Fixture
    # setUp(): 테스트 메소드가 호출되기 전에 상태를 재설정 할 수 있는 기회를 제공(초기화)
    # tearDown(): 테스트가 끝난 후 정리를 수행 할 수 있는 기회를 제공(해제)
   ####
    def setUp(self): # 단위 테스트가 개발에 사용하는 일반 데이터베이스를 사용하지 못하도록 serUp()에서 약간의 해킹을 구현
        #app.config['SQLALCHEMY_DATABASE_URI']  = 'sqlite://' 
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all() # 모든 데이터베이스 테이블을 만듦 -> 테스트에 유용한 데이터베이스를 처음부터 빠르게 만드는 방법 


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop() ## 
    
    def test_password_hasing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))
    
    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(),[])  # aseertEqual(결과 값, 기대한 값) 
        self.assertEqual(u1.followers.all(),[])

        u1.follow(u2)  # u1이 u2를 follow
        db.session.commit()
        self.assertTrue(u1.is_following(u2)) # u1이 u2를 following 하는지 
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username,  'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_poasts(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john",  author=u1, timestamp =now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2, timestamp =now + timedelta(seconds=4))
        p3 = Post(body="post from mary",  author=u3, timestamp =now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4, timestamp =now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()
        
        # setup the followers
        u1.follow(u2) # john follows susan
        u1.follow(u4) # john follows david
        u2.follow(u3) # susan follows mary
        u3.follow(u4) # mary follows david
        db.session.commit()

        # check the followed posts of user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

if __name__ == '__main__':

    unittest.main(verbosity=2)  #### verbosity=2  ** 2(verbose)
    # __name__ 내장변수 : 현재 모듈의 이름을 담고 있는 내장 변수.
    # 직접 실행된 모듈의 경우 __main__이라는 값을 가지게 되며,
    # 직접 실행되지 않은 import된 모듈은 모듈의 이름(파일명)을 가지게 된다. 
    # https://medium.com/@chullino/if-name-main-%EC%9D%80-%EC%99%9C-%ED%95%84%EC%9A%94%ED%95%A0%EA%B9%8C-bc48cba7f720

    """
    0 (조용함) : 실행 된 총 테스트 수와 전체 결과를 얻습니다.
    1 (기본값) : 모든 성공적인 테스트에 대해 동일한 플러스 점 또는 모든 실패에 대해 F를 얻습니다.
    2 (verbose) : 모든 테스트의 도움말 문자열과 결과를 얻습니다.   (-v)
    """


"""
@ unittest -  Python에 포함된 다양한 테스트를 자동화할 수 있는 기능이 포함되어 있는 표준 라이브러리
@unittest에 포함된 주요 개념
    * Testcase :unittest 프레임 워크의 테스트 조직의 기본 단위
    * FixTure  
        - 테스트함수의 전 또는 후에 실행
        - 테스트가 실행되기 전에 테스트 환경이 예상 된 상태에 있는지 확인하는데 사용
        - 테스트 전에 데이터베이스 테이블을 만들거나 테스트 후에 사용한 리소스를 정리하는데 사용
    * assertion 
        - unittest가 테스트가 통과하는지 또는 실패 하는지를 결정.
        - bool test, 객체의 적합성, 적절한 예외 발생 등 다양한 점검을 할 수 있음
        - assertion이 실패하면 테스트 함수가 실패함.
- 테스트 메소드는 메소드명 앞에 test접두어를 붙여줘야됨.
\
"""

