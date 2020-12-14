# pylint: disable=no-member
from flask import render_template
from app import db
from app.errors import bp

# 사용자 정의 오류 페이지
# @errorhandler 데코레이터를 사용하여 해당 템플릿의 내용에 대한 오류 반환 
#@app.errorhandler(404)
@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404 # 템플릿 뒤 두 번째 값 반환 (오류 코드 번호)

#@app.errorhandler(500)
@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()  
        # 실패한 데이터베이스 세션이 템플릿에 의해 트리거 된 데이터베이스 액세스를 방해하지 않도록 세션 롤백 실행 -> 세션이 깨끗한 상태로 재설정됨
    return render_template('500.html'), 500

#### Blueprint
## @app.errorhandler 데코레이터를 사용하여 애플리케이션에 오류 핸들러를 연결하는 대신
## 블루프린트의 @bp.errorhandler 데코레이터를 사용.
#  두 데코레이터가 동일한 최종 결과를 얻지만 아이디어는 블루 프린트를 애플리케이션과 독립적으로 만들어
#   더 이식 가능하게 만드는 것.
