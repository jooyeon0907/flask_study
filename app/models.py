# 데이터베이스와 관련된 코드
# pylint: disable=no-member
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash , check_password_hash # password 암호화를 위해 사용 
from flask_login import UserMixin
from app import login
from hashlib import md5 # 사용자 아바타 URL

#사용자 로더 기능 - 애플리케이션이 ID가 주어진 사용자를 로드하기 위해 호출 할 수 있는 사용자 로더 기능 구성
@login.user_loader
def load_user(id):
    return User.query.get(int(id)) # 문자열을 정소로 변환 할 필요가 있도록 인수가 문자열이 될 것.


class User(UserMixin, db.Model): # 만들 데이터 모델을 나타내는 객체 선언 , SQLAchmey의 기능을 사용하기 위해 db.Model을 상속받는다.
   ##  __table_name__ = 'user' : 테이블 이름은 자동으로 정의되지만 __table_name__을 이용해 명시적으로 정할 수 있다.  

    # 만들 데이터 모델을 선언하였으니 모델의 필드명과 필드와 관련된 제약사항들을 정의한다. 
    # 필드 정의는 db.column()을 사용 ->  필드명 = db.Cloumn(필드와 관련된 제약사항(데이터타입, 키 설정 등,,))
    id = db.Column(db.Integer, primary_key=True)  #'id' 필드는 대부분의 모델에서 기본 키로 사용한다. (primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True) # 최대 길이를 명시하여 공간 절약 -> String(64) , 'username'과 'email'은 서로 중복되지 않아야 함(unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
   # user테이블과 post케이블의 관계를 명시해줌  # db.relationship(연결된 객체명, backref=가상 필드명, loding relationship)
    posts = db.relationship('Post', backref='author', lazy='dynamic') 
        # 사용자가 작성했던 모든 게시물에 대한 정보는 user.posts를 이용해 접근할 수 있으며
        # 이 게시물을 작성한 게시자를 post.author 를 이용해 접근할 수 있음

    def __repr__(self):  # __repr__(self) :객체를 나타내는 공식적인 문자열로 repr()로 호출할 수 있음 . 디버깅에 유용
        return f'<User {self.username}>'


    ## 비밀번호 해싱 및 확인
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 사용자 아바타 URL
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest() 
        # MD5 해시를 생성하려면 Gravatar 서비스에 필요한 이메일을 소문자로 변환 
        # -> Python의 MD5 지원은 문자열이 아닌 바이트에서 작동하기 때문에 해시 함수에 전달하기 전에 문자열을 바이트로 인코딩
        return f'https://www.gravatar.com./avatar/{digest}?d=identicon&s={size}' # 요청된 크기(픽셀)로 조정된 사용자 아바타 이미지의 URL을 반환
                                                                                # 아바타가 등록되지 않은 사용자의 경우 idention 이미지가 생성

    # 사용자 모델의 새 필드
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    ## 필드가 추가되었기 대문에 flask db migrate & flask updade 를 진행 해줘야됨





class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) # 게시일의 경우에는 기본값을 'datetime.utcnow()'를 사용함으로써 명시적으로 게시일을 나타내지 않은 경우 현재시간을 게시해줌
    # user테이블의 id를 외래키로 하는 user_id     #'테이블명.필드명'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 

    def __repr__(self):
        return '<Post {}>'.format(self.body)