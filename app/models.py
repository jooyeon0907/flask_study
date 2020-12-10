# 데이터베이스와 관련된 코드
# pylint: disable=no-member
from datetime import datetime
from app import db , app
from werkzeug.security import generate_password_hash , check_password_hash # password 암호화를 위해 사용 
from flask_login import UserMixin
from app import login
from hashlib import md5 # 사용자 아바타 URL
from time import time
import jwt



# 추종자 연관 테이블
# 외래 키 외에 데이터가 없는 보조 테이블이므로 연결된 모델 클래스 없이 만듦.
#   -> 보조 테이블의 경우 모델을 사용하지 않고 실제 테이블을 사용하는 것이 좋다. 
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

###### ???  type 알아내기 -> ex) type(u.about_me)
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

    # 프로필에 사용 될 새 필드 추가
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    ## 필드가 추가되었기 대문에 flask db migrate & flask updade 를 진행 해줘야됨

    # user 테이블에서 다:다 관계 선언하기
    followed = db.relationship(
        'User', # 관계를 오른쪽 엔티티.(왼쪽 엔터티는 상위클래스). 자기 참조 관계이기 때문에 양쪽에서 동일한 클래스를 사용해야함.
        secondary=followers, # 위에 정의한 관계에 사용되는 연관 테이블을 구성 
        primaryjoin=(followers.c.follower_id == id), # 왼쪽 엔티티(팔로워 사용자)를 연관  테이블과 연결하는 조건을 나타냄. 
                                                     #  관계의 왼쪽에 대한 결합 조건 follower_id는 연관 테이블의 필드와 일치하는 사용자ID
        secondaryjoin=(followers.c.followed_id == id), # 오른쪽 엔티티(팔로잉 사용자)를 연관 테이블과 연견하는 조건을 나타냄.
                                                        # primaryjoin과 비슷하지만 유일하게 다른 점은 연결 테이블의 다른 왜래키이다.
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic' ) # 오른쪽 엔티티에서 이 관계에 액세서하는 방법을 정의.
                                                                          # 왼쪽 - followerd, 오른쪽 - followers를 사용하여 오른쪽의 대상 사용자에 연결된 모든 왼쪽 사용자를 나타냄.
                                                                          # 추가된 lazy 인수는 이 쿼리의 실행모드를 나타냄 - dynamic 특정 요청이 있을때까지 쿼리가 실행되지 않도록 설정하는 모드. 일대 다 관계를 설정하는 방법이기도 함.


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
   
    # 팔로워 추가 및 제거
    def follow(self, user): 
        if not self.is_following(user):# Flase이면 팔로잉 안한 상태이므로 추가 
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user): # True이면 팔로잉 되어있는 상태여서 삭제할 유저가 있으므로 진행됨
            self.followed.remove(user)
    
    def is_following(self, user): # 두 사용자 간의 링크가 이미 존재하는지 확인
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0  # 유저가 팔로워한 사람 중 포함 되어있으면 True 아니면 Flase 반환
        # 왼쪽 외래키가 self사용자로 설정, 오른쪽이 user 인수로 설정된 연관 테이블의 항목을 찾음. 
        # 이 쿼리의 결과는 0 또는 1이므로 존재 유무 판단함 

    # 팔로우 한 사용자로부터 게시물 얻기
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

        #  Post.query.join(...).filter(...).order_by(...)
       
        ## join
        #  Post.query.join( followers, (followers.c.followerd_id == Poast.user_id))
        #  -> posts 테이블에서 조인 작업을 호출 
        # 첫 번째 인수는 팔로워 연관 테이블, 두번째 인수는 결합 조건 
        # 데이터베이스가 게시물과 팔로워 테이블의 데이터를 결합하는 임시 테이블을 생성 -> 인수로 전달한 조건에 따라 데이터가 병합됨.
        # followers 테이블의 followed_id 값과 posts 테이블의 user_id 값이 같아야 한다.
        # posts 테이블(조인의 왼쪽)에서 각 레코드를 가져와 followers 조건과 일치하는 테이블 (조인의 오른쪽)에서 모든 레코드를 추가
        # followers는 조건과 일치하는 여러 레코드가 있으며 각각에 대해 게시 항목이 반복됨 (외래키-Foregina Key)
        # 특정 게시물에 대해 팔로워가 일치하지 않는 경우 해당 게시물 레코드는 조인의 일부가 아님 (기본키 - Primary Key)
       
        ## filter
        # filter(followers.c.follower_id == self.id)
        # 이 쿼리는 User 클래스 메서드에 있으므로 self.id는 내가 관심있는 사용자의 id를 참조한다.
        # filter() 호출은 follower_id 사용자로 설정된 열이 있는 조인 된 테이블의 항목을 선택 -> 현재 유저가 팔로워하고 있는 항목만 유지 
        
        ## sorting
        # order_by(Post.timestamp.desc())
        # 프로세스의 마지막 단계 -> 결과를 정렬하는 것 
        # desc() - 내림차순으로 정렬 -> 가장 최근의 블로그 게시물순
        
        # union
        # 두 SQL 쿼리문의 결과를 합치는 연산자
        # UNION은 행의 모든 값이 일치하는 중복된 행이 제외됨
        # UNION ALL은 중복된 행이 그대로 있음

    ## 비밀번호 토큰 생성 및 확인 기능 - 토큰은 사용자의 소유이므로 User 모델의 메소드로 작성
    def get_reset_password_token(self, expires_in=600): # expires_in : 토큰 ㅏㄴ료 시간 
        return jwt.encode(
            {'reset_password':self.id, 'exp': time() + expires_in}, # 암호 재설정 토큰에 사용할 페이로드는 형식 -> {'reset_password':user_id, 'exp' :token_expration} 
                                                                    # exp 필드는 JWT의 표준이며 존재하는 경우 토큰의 만료시간을 나타냄 
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8') 
            # 토큰의 보안을 유지하려면 암호화 서명을 만드는데 사용할 비밀 키를 제공해야함. -> config.py에 구성된 비밀키 제공하기
            # algorithm 인수는 토큰 생성 방법을 지정 -> HS256 알고리즘이 가장 널리 사용됨.

     # JWT 토큰을 문자열로 생성 
     # jwt.encode() 함수는 토큰을 바이트 시퀀스로 반환하는데 응용프로그램에서는 
     # 토큰을 문자열로 사용하는 것이 더 편리하기 때문에 decode('utf-8')을 사용한다.
     # ** 인코딩 - 문자열을 바이트코드로 변환함. encode = 코드화 = 암호화
     #   -> 파이썬에서 문자열은 유니코드로처리 - 유니코드를 utf-8, euc-kr, ascii 형식의 byte코드로 변환함을 의미
     # ** 디코딩 - 바이트를 문자열로 변환. decode = 역 코드화 = 복호화
     #          - utf-8, euc-kr, ascii 형식의 byte코드를 문자열로 변환 
    
    # 토큰을 안전하게 만드는 것은  페이로드가 서명된다는 것 
    # 누군가 토큰의 페이로드를 위조하거나 변조하려고 하면 서명이 무효화 되고 새 서명을 생성하려면 비밀 키가 필요함. 
    # 토큰이 확인되면 페이로드의 내용이 디코딩되어 호출자에게 다시 반환됨.
    # 토큰의 서명이 검증 된 경우 페이로드를 인증 된 것으로 신뢰할 수 있음.

    # 암호 재설정 토큰에 사용할 페이로드 형식 -  {'reset_password':user_id, 'exp' :token_expration} 
    # 사용자가 이메일 링크를 클릭하면 토큰이 URL의 일부로 애플리케이션에 다시 전송되며 
    #  이 URL을 처리하는 보기 기능이 가장 먼저 수행하는 작업은 이를 확인 하는 것
    # 서명이 유효하면 페이로드에 저장된 ID로 사용자를 식별 할 수 있다.
    # 사용자의 신원이 확인되면 애플리케이션은 새 비밀번호를 요청하고 사용자 계정에 설정할 수 있다.

    ## 토큰 확인 방법
    @staticmethod
    def verify_reset_password_token(token):
        try:  
          # 토큰을 가져와 PyJWT의 jwt.decode() 함수를 호출하여 디코딩을 시도.
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithm=['HS256'])['reset_password']
          # 토큰이 유효하면 토큰 페이로드의 reset_password 키 값이 사용자의 id이므로 사용자를 로드하고 반환 할 수 있음.
           
            print(f'verify_reset_password_token(token): >>>>>{id}')
            print(f'verify_reset_password_token(token): >>>>>{User.query.get(id)}')
        except:
      # 토큰의 유효성을 검사 할 수 없거나 만료되면 예외가 발생하고 이 경우 오류를 방지하기 위해 포착한 다음 None을 호출자에게 반환
            return
        return User.query.get(id)
    # verify_reset_password_token()은 정적 메서드이므로 클래스에서 직접 호출 할 수 있다.
    # 정적 메서드(staticmethod)는 클래스를 첫번째 인수로 받지 않는다.(slef를 받지 않으므로 인스턴스 속송에 접근 X )
    #   -> 인스턴스 내용과는 상관없이 결과만 구할때 사용.  # https://dojang.io/mod/page/view.php?id=2379
        
        
        
## 사용자 로더 기능 - 애플리케이션이 ID가 주어진 사용자를 로드하기 위해 호출 할 수 있는 사용자 로더 기능 구성
@login.user_loader
def load_usber(id):
    return User.query.get(int(id)) # 문자열을 정소로 변환 할 필요가 있도록 인수가 문자열이 될 것.
#### -> 이 데코레이터가 젤 위에 있었을때 회원가입 오류남 
#  flask-SQLAlchemy OperationalError: (sqlite3.OperationalError) no such table




class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) # 게시일의 경우에는 기본값을 'datetime.utcnow()'를 사용함으로써 명시적으로 게시일을 나타내지 않은 경우 현재시간을 게시해줌
    # user테이블의 id를 외래키로 하는 user_id     #'테이블명.필드명'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 

    def __repr__(self):
        return '<Post {}>'.format(self.body)











