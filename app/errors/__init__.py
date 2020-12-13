# blueprint creation 
from flask import Blueprint

bp = Blueprint('errors',__name__)

from app.errors import handlers
# blueprint 객체가 생성된 후 handlers.py 모듈을 임포트하여 
# 그 안에 있는 오류 핸들러가 블루 프린트에 등록됨 
# 순환 종속성을 피하기 위해 맨 아래에 두기