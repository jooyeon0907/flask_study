from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # is_authenticated : True 사용자가 유효한 자격 증명을 가지고 있는지 여부를 나타내는 속성. 사용자의 로그인 여부 확인.
        return redirect(url_for('main.index'))   # 사용자가 이미 로그인되어 있으면 인덱스 페이지로 redirect함 
    form = LoginForm() ####
    if form.validate_on_submit(): 
        user = User.query.filter_by(username=form.username.data).first() # filter_by() -  결과물을 필터링
                                                                # first() - 결과가 1개 or 0개 뿐이므로 사용자 개체가 있거나 없는 경우 none 반환. 하나의 결과만 필요로할 때 쿼리 실행 
        if user is None or not user.check_password(form.password.data): #  
            flash('Invalid username or passsword')  # flash() - 사용자에게 메시지를 표시하는 유용한 방법
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data) # 이름과 비번이 모두 일치시 login_user() 호출 
       
        next_page = request.args.get('next') 
        # URL이 상대적인지 절대적인지 확인하기 위해 werkzeug의 url_parse() 함수로 구문 분석한 다음 net loc 구성요소가 설정되었는지 확인 (애플리케이션 보안을 강화하기 위함)
        if not next_page or url_parse(next_page).netloc != '': 
            next_page = url_for('main.index')    # 로그인 URL에 next 인수가 없으면 사용자는 인덱스 페이지로 리디렉션 
        return redirect(next_page)  # redirect() - 클라이언트 웹 브라우저가 인수로 지정된 다른 페이지로 자동으로 이동하도록 지시. 사용자를 애플리케이션의 색인 페이지로 리디렉션함.
    return render_template('auth/login.html',  title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index')) # url_for('index') : index 함수에 대한 url을 얻어냄.


# 사용자 등록하기
@bp.route('/register', methods=['GET', 'POST'])
def register():
    # 로그인이 되어있는 경우 index로 리다이렉트 시킴
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm() # 회원가입 폼 불러오기
    # 정상적인 입력값으로 확인되면 회원정보 DB에 정보 추가하기 
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)



## 비밀번호 재설정 요청보기 기능.
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:  # 인증된 유저라면
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    # user = User.query.filter_by(email=form.email.data).first()
    # print(f'::::::::::::::/reset_password_request >>>>{form.email.data}')
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(f'/:::::::reset_password_request >>>> user : {user}')
        if user: # 존재하는 email이라면
            send_password_reset_email(user)  
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', 
                            title='Reset Password', form=form )


## 비밀번호 재설정 보기 기능.
@bp.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token) # 토큰 확인 방법을 호출하여 사용자가 누구인지 확인하기
    if not user: # 토큰 사용 결과 인증 실패시 
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    print(f'!!!!!!%%%% reset_password %%%%!!!!!!!!!! {user}')
    if form.validate_on_submit():
        user.set_password(form.password.data) # 비밀번호 재설정
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

