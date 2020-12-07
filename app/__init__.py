from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app) # 로그인  초기화
login.login_view = 'login' # Flask-Login에서 로그인 처리하는 보기 기능. 즉, url_for() URL 을 가져오기 위해 호출에 사용할 이름.
# routes와 데이터베이스 구조 정의하는 models 호출
from app import routes, models
