# pylint: disable=no-member
from flask import render_template
from app import app, db

# 사용자 정의 오류 페이지
# @errorhandler 데코레이터를 사용하여 해당 템플릿의 내용에 대한 오류 반환 
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404 # 템플릿 뒤 두 번째 값 반환 (오류 코드 번호)

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  
        # 실패한 데이터베이스 세션이 템플릿에 의해 트리거 된 데이터베이스 액세스를 방해하지 않도록 세션 롤백 실행 -> 세션이 깨끗한 상태로 재설정됨
    return render_template('500.html'), 500