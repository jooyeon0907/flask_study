# pylint: disable=no-member
from flask import render_template ,flash, redirect, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from flask import request
from werkzeug.urls import url_parse
from datetime import datetime

## route - uri를 정리해주는 것 
@app.route('/')
@app.route('/index')
@login_required # Flask-Login이 익명 사용자로부터 뷰 기능을 데코레이터로 보호.
                # @app.route 아래에 있는 뷰 함수에 추가하면 함수가 보호되고(/index 접근 유저는 인증된 유저여야만 함.), 인증되지 않은 사용자에게 액세스를 허용X 로그인이 필요한 페이지로 설정.
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home Page', posts=posts)
 # 렌더링 - 템플릿을 완전한 HTML 페이지로 변환하는 작업 
        # render_template() - {{ ... }} 블록을 render_template() 호출에 제공된 인수로 해당 값 대체
        #                   - 첫 번째 아규먼트로 렌더링 할 html 파일명을 넘겨주고, 그 이후에는 html 파일에 전달한 변수를 넘겨줌 



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # is_authenticated : True 사용자가 유효한 자격 증명을 가지고 있는지 여부를 나타내는 속성. 사용자의 로그인 여부 확인.
        return redirect(url_for('index'))   # 사용자가 이미 로그인되어 있으면 인덱스 페이지로 redirect함 
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first() # filter_by() -  결과물을 필터링
                                                                # first() - 결과가 1개 or 0개 뿐이므로 사용자 개체가 있거나 없는 경우 none 반환. 하나의 결과만 필요로할 때 쿼리 실행 
        if user is None or not user.check_password(form.password.data): #  
            flash('Invalid username or passsword')  # flash() - 사용자에게 메시지를 표시하는 유용한 방법
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data) # 이름과 비번이 모두 일치시 login_user() 호출 
                                                         # -> 사용자가 로그인된 상태로 등록하므로 사용자가 탐색하는 향후 페이지에 해당 사용자에 대한 current_user 변수가 설정됨
        next_page = request.args.get('next') 
        if not next_page or url_parse(next_page).netloc != '': # URL이 상대적인지 절대적인지 확인하기 위해 werkzeug의 url_parse() 함수로 구문 분석한 다음 net loc 구성요소가 설정되었는지 확인 (애플리케이션 보안을 강화하기 위함)
            next_page = url_for('index')    # 로그인 URL에 next 인수가 없으면 사용자는 인덱스 페이지로 리디렉션 
        return redirect(next_page)  # redirect() - 클라이언트 웹 브라우저가 인수로 지정된 다른 페이지로 자동으로 이동하도록 지시. 사용자를 애플리케이션의 색인 페이지로 리디렉션함.
    return render_template('login.html',  title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# 사용자 등록하기
@app.route('/register', methods=['GET', 'POST'])
def register():
    # 로그인이 되어있는 경우 index로 리다이렉트 시킴
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm() # 회원가입 폼 불러오기
    # 정상적인 입력값으로 확인되면 회원정보 DB에 정보 추가하기 
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# 사용자 프로필보기 기능
@app.route('/user/<username>') # <username> : 동적 구성 요소 , 사용자 이름으롤 쿼리를 사용하여 데이터베이스에서 사용자를 로드
@login_required
def user(username):
    # username에 맞는 값 가져오기 시도하여 성공하면 결과 가지고, 실패하면 404 에러 페이지 출력 
    #   -> 사용자 이름이 데이터베이스에 존재하지 않으면 함수가 반환되지 않고 대신 404예외가 발생하기 때문에 쿼리가 사용자를 반환했는지 확인하지 않아도 됨.
    user = User.query.filter_by(username=username).first_or_404()
    # posts에 출력될 데이터 넣기
    posts = [
        {'author':user, 'body': 'Test Post #1'},
        {'author':user, 'body': 'Test Post #2'}
    ]
    # 성공하면 user 변수를 user에 넣고, posts 변수를 posts에 넣어 user.html 열기
    return render_template('user.html', user=user, posts=posts)


# 마지막 방문 시간 기록
@app.before_request # before_request 데코레이터는 뷰 함 수 바로 전에 실행할 데코 레이팅 된 함수를 등록 
                    #-> request 되기 전에, 즉 웹페이지가 view가 출력되기 전에 실행하려는 코드를 이곳에 삽입
def before_request():
    # current_user가 로그인 되어있는지 확인하고 last_seen 필드를 현재 시간으로 설정 
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        # 커미하기 전 db.session.add()가 없는 이유? Flask-Login이 사용자 로더 콜백 함수를 호출하여 대상 사용자를 데이터베이스 세션에 넣는 데이터베이스 쿼리를 실행한다.




