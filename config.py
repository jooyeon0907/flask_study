import os

from dotenv import load_dotenv ## 

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(basedir, 'config.env'))  ###

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'  # 양식을 보호하기 위해 비밀키 구성하기

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 이메일 구성 
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # -> 5개의 구성 변수는 해당 환경 변수 대응 요소에서 제공
    ADMINS = ['shin.jooyeon@ahope.co.kr']  # 오류 보고서를 받을 주소
