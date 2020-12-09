import os

from dotenv import load_dotenv ## 

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(basedir, 'config.env'))  ###

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'  # 양식을 보호하기 위해 비밀키 구성하기

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


