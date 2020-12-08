# pylint: disable=no-member
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging 
from logging.handlers import SMTPHandler, RotatingFileHandler # SMTPHandler - 오류시 이메일 보내기 , RotatingFileHandler - 파일 기반 로그 활성화
import os



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app) # 로그인  초기화
login.login_view = 'login' # Flask-Login에서 로그인 처리하는 보기 기능. 즉, url_for() URL 을 가져오기 위해 호출에 사용할 이름.
# routes와 데이터베이스 구조 정의하는 models 호출


if not app.debug:
    # 이메일 오류 기록
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


    # 파일에 로깅
    if not os.path.exists('logs'):  # logs 존재하지 않는 경우 생성
        os.mkdir('logs')
   # log 출력 형식
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10) # log 파일 정보 설정 : 로그파일의 크기를 10KB로 제한하고 마지막 10개의 로그 파일을 백업으로 유지함.
                # RotatingFileHandler 클래스는 로그를 회전하여 애플리케이션이 장시간 실행될 때 로그 파일이 너무 커지지 않도록 함. 
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')) # 타임스탬프,  로깅수준, 메시지 및 소스파일과 로그 항목이 시작된 줄 번호를 포함하는 형식. # asctime 시간 ,name 로거이름,levelname 로깅레벨, message 메세지 
                # logging.Formatter 클래스는 로그 메시지에 대한 사용자 지정 형식을 제공해줌.
   
    # log 출력 기준 설정
    file_handler.setLevel(logging.INFO)  
    app.logger.addHandler(file_handler) 
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')
    
    # 로깅 레벨 
    # 로깅 범주 DEBUG < INFO < WARNING < ERROR < CRITICAL
    """
    # TRACE : 추적 레벨은 Debug보다 좀더 상세한 정보를 나타냄
    # DEBUG : 프로그램을 디버깅하기 위한 정보 지정
    # INFO :  상태변경과 같은 정보성 메시지를 나타냄 
    # WARN :  처리 가능한 문제, 향후 시스템 에러의 원인이 될 수 있는 경고성 메시지를 나타냄 
    # ERROR :  요청을 처리하는 중 문제가 발생한 경우
    # FATAL :  아주 심각한 에러가 발생한 상태, 시스템적으로 심각한 문제가 발생해서 어플리케이션 작동이 불가능할 경우

    """


# 순환 임포트
from app import routes, models, errors  
# errors -  오류 핸들러 가져오기 
