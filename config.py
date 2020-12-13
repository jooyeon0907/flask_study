import os

from dotenv import load_dotenv ## 

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(basedir, 'config.env'))  ## .env 파일 불러오기

# 구성 변수 설정하기
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' 
    # 양식을 보호하기 위해 비밀키 구성하기 **Flaskk 애플리케이션에서 중요한 부분!
    # Flask-WTF 확장은 이를 사용하여 CSRF의 공격으로부터 웹 양식을 보호함.
    # SECRET_KEY라고 하는 환경 변수의 값을 찾기 or 하드 코딩 된 문자열 (환경이 변수를 정의하지 않으면 하드 코딩된 문자열이 대신 사용됨)
    # 연습용으로 보안 요구사항을 낮게 설정했지만, 
    #  응용 프로그램이 프로덕션 서버에 배포될 때 환경에서 고유하고 추측하기 어려운 값을 설정하여 서버가 다른 사람이 알 수 없는 보안키를 갖도록 함

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # DATABASE_URI 환경변수에서 데이터베이스 URL을 가져오고 정의되지 않는 경우,
    # 변수에서 저장되는 기본 디렉터리 app.db 라는 데이터베이스를 구성한다
    # SQLALCHEMY_DATABASE_URI : 연결에 사용해야하는 데이터베이스 URL
    # SQLALCHEMY_TRACK_MODIFICATIONS : Flask-SQLALchemy가 True로 설정하면 개체수정을 추적하고 신호를 내보냄.
    #                                    기본값은 None이며 추적을 활성화하지만 향후 기본적으로 비활성화 될 것이라는 경고를 표시
    #                                    추가 메모리가 필요하며 필요하지 않은 겨우 비활성화 (대부분 비활성화하여 시스템 리소스 절약)
                                       
    """
    >>> db
    <SQLAlchemy engine=sqlite:////home/ahope/jooyeon/flask_study/flask_prac2/microblog/app.db>
    """


    # 이메일 구성 
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # -> 5개의 구성 변수는 해당 환경 변수 대응 요소에서 제공
    ADMINS = ['shin.jooyeon@ahope.co.kr']  # 오류 보고서를 받을 주소


    # 페이지 구성 당 게시물 수 
    POSTS_PER_PAGE = 3
    """
    쿼리 문자열 인수를 사용하여 선택적 페이지 번호 지정하기. 지정되지 않은 경우 기본 값은 1페이지
    EX)
    페이지 1, 암시 적 : http : // localhost : 5000 / explore
    페이지 1, 명시 적 : http : // localhost : 5000 / index? page = 1
    페이지 3 : http : // localhost : 5000 / index? page = 3
    """
    
    # 지원되는 언어 목록을 추적하기
    LANGUAGES = ['en', 'es']

    # Microsoft Translator 키를 추가
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY') 
    
