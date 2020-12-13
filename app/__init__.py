# pylint: disable=no-member
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging 
from logging.handlers import SMTPHandler, RotatingFileHandler # SMTPHandler - 오류시 이메일 보내기 , RotatingFileHandler - 파일 기반 로그 활성화
import os
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel
from flask import request 
from flask_babel import lazy_gettext as _l
from config import Config
from flask import current_app

## 초기화
# 모든 Flask 애플리케이션은 '애플리케이션 인스턴스'를 생성해야 한다.
# 웹 서버는 클라이언트로부터 수신한 모든 request를 오브젝트에서 처리하는데
#   이때 웹 서버 게이트웨이 인터페이스(Web Server Gateway Interfase)라는 프로토콜을 사용함. - WSGI
#   WSGI : 파이썬에서 어플리케이션, 즉 파이썬 스크립트(웹 어플리케이션)가 웹 서버와 통신하기 위한 인터페이스 (프로토콜 개념으로 이해할 수 있음 )


db = SQLAlchemy()
migrate = Migrate()

login = LoginManager() # 로그인  초기화
login.login_view = 'auth.login' # Flask-Login에서 로그인 처리하는 보기 기능. 즉, url_for() URL 을 가져오기 위해 호출에 사용할 이름.
# routes와 데이터베이스 구조 정의하는 models 호출
login.login_message = _l('Please log in to access this page.')




# Flask-Mail 인스턴스 생성
#  - Flask 확장과 마찬가지로 Flask-Mail 확장도 Flask 애플리케이션을 만든 직후 인스턴스를 만들어야하기 때문에 __init__.py에 작성
mail = Mail()

bootstrap = Bootstrap()
# Flask-Bootstrap 확장이 초기화되면 
#   - bootstrap /base.html 템플릿이 사용 가능해지며 
#   - extends 절이 있는 애플리 케이션 템플릿에서 참조 될 수 있음

moment = Moment()
# 다른 확장과 달리 Flask-Momonet는 moment.js 와 함께 작동하므로 애플리케이션의 모든 템플릿에는 라이브러리가 포함되어야함.
# 수행하는 방법 1. 라이브러리를 가져오는 <script>태그를 명시적으로 추가
#              2. <script>태그를 생성하는 moment.include_moment()함수를 노출하여 더 쉽게 만듦.

babel = Babel()



##
def create_app(config_class=Config):
    app = Flask(__name__) # 애플리케이션 인스턴스는 Flask클래스의 오브젝트이다. 
                      # Flask 클래스 생성자에 필요한 인자는 메인 모듈의 이름이나 애플리케이션 패키지 이름이다.
                      #     대부분의 어플리케이션에서는 파이썬의 __name__ 변수가 적절한 값. 
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    # error 블루프린트 등록하기
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    # ***블루프린트를 등록하기 위해 Flask 애플리케이션 인스턴스의 register_blueprint() 메서드가 사용됨
    # 블루프린트가 등록되면 모든 뷰 함수, 템플릿, 정적 파일, 오류 처리기 등이 애플리케이션에 연결됨.
    # 순환 종속성을 피하기 위해 블루 프린트 가져오기를 app.register_blueprint() 바로 위에 놓음.

    # auth 블루프린트 등록하기
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    # register_bluteprint() 호출에는 url_prefix 인수  (필수는 X 선택사항)
    #  -> 블루프린트에 정의 된 모든 경로는 URL에서 이 접두사('/auth'를 가져온다
    #  ex) http://localhost:5000/auth/login

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:  # - not app.testing 절을 추가하여 단위 테스트 중에 모든 로깅을 건너 뜀
        ## 이메일 오류 기록
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(  # 1. SMTPHandler 인스턴스 만들기
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR) # 2. 오류만 보고하도록 로깅수준 설정 
            app.logger.addHandler(mail_handler)

        ## 파일에 로깅
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
        
        #app.logger.setLevel(logging.INFO)
        #app.logger.info('Microblog startup')
        
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
    return app

# 각 요청에 대해 호출되어 해당 요청에 사용할 언어 번역을 선택
@babel.localeselector
def get_locale():
   return request.accept_languages.best_match(current_app.config['LANGUAGES'])
  # return 'es'  # best_match() 없이 반환값을  바로 설정하기
# accept_languages : Flask의 request 객체 속성
# 클라이언트가 요청과 함께 보내는 Accept-Language 헤더와 함께 작동하는 고급 인터페이스를 제공
# Accept-Language 헤더는 클라이언트 언어 및 로케일 기본 설정을 가중치 목록으로 지정.
# 이 헤더의 내용은 브라우저의 기본 설정 페이지에서 구성할 수 있으며 기본값은 일반적으로 컴퓨터 운영 체제의 언어 설정에 가져온다.
#			-> 선호자가 선호하는 언어 목록을 제공 할 수 있으므로 유용함.




# 순환 임포트
#from app import routes, models, errors # errors -  오류 핸들러 가져오기 
from app import models

