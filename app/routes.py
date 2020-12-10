# pylint: disable=no-member
from flask import render_template ,flash, redirect, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User ,Post
from flask import request
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email
from app.forms import ResetPasswordRequestForm, ResetPasswordForm


## route - uri를 정리해주는 것 
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required # Flask-Login이 익명 사용자로부터 뷰 기능을 데코레이터로 보호.
                # @app.route 아래에 있는 뷰 함수에 추가하면 함수가 보호되고(/index 접근 유저는 인증된 유저여야만 함.), 인증되지 않은 사용자에게 액세스를 허용X 로그인이 필요한 페이지로 설정.
def index():
    form = PostForm()   # 게시글 작성하기 폼
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
        # 웹 양식을 제출한 후 사용자가 실수로 페이지를 새로고침할 때 중복으로 게시물이 삽입되지 않도록 하기 위해 
        # redirection으로 응답해줌 -> Post/Redirect/Get 패턴  (그래서 POST,GET 두 경로에서 요청을 수락하도록 설정함 )
        # ==> POST 요청이 리디렉션으로 응답되면 이제 브라우저는 리디렉션에 표시된 페이지를 가져오기 위해 
        #     GET 요청을 보내도록 지시 받으므로 마지막 요청은 더 이상 POST 요청이 아님 -> 새로 고침할 때 중복 게시물 삽입되는 것을 방지
    """
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
    """
    # posts = current_user.followed_posts().all() # 팔로우한 유저의 게시글들 가져오기
    # 페이지 매김해서 게시글 가져오기 
    page = request.args.get('page', 1 ,type=int)     # 1. page 쿼리 문자열 인수 또는 기본값 1에서 표시할 페이지 번호를 결정한 다음, 
    posts = current_user.followed_posts().paginate(  # 2. 원하는 결과 페이지만 검색하기 위해 paginate() 메서드 사용
        page, app.config['POSTS_PER_PAGE'], False)    # 페이지 크기를 결정하는 POSTS_PER_PAGE 구성 항목은 app.config 개체를 통해 액세스됩니다.
    
    # 다음 및 이전 페이지 링크 생성하기
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
     # view 함수의 next_url 및 prev_url은 (Flask-SQLAlchemy의 Pagination 클래스 객체에 있음)
     # 해당 방향에 페이지가 있는 경우에만 url_for()에서 반환하는 URL로 설정.
                
    return render_template('index.html', title='Home Page', form=form, posts=posts.items, 
                                                            next_url=next_url, prev_url=prev_url)
        # 렌더링 - 템플릿을 완전한 HTML 페이지로 변환하는 작업 
        # render_template() - {{ ... }} 블록을 render_template() 호출에 제공된 인수로 해당 값 대체
        #                   - 첫 번째 아규먼트로 렌더링 할 html 파일명을 넘겨주고, 그 이후에는 html 파일에 전달한 변수를 넘겨줌 

    



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # is_authenticated : True 사용자가 유효한 자격 증명을 가지고 있는지 여부를 나타내는 속성. 사용자의 로그인 여부 확인.
        return redirect(url_for('index'))   # 사용자가 이미 로그인되어 있으면 인덱스 페이지로 redirect함 
    form = LoginForm() ####
    if form.validate_on_submit(): 
        user = User.query.filter_by(username=form.username.data).first() # filter_by() -  결과물을 필터링
                                                                # first() - 결과가 1개 or 0개 뿐이므로 사용자 개체가 있거나 없는 경우 none 반환. 하나의 결과만 필요로할 때 쿼리 실행 
        if user is None or not user.check_password(form.password.data): #  
            flash('Invalid username or passsword')  # flash() - 사용자에게 메시지를 표시하는 유용한 방법
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data) # 이름과 비번이 모두 일치시 login_user() 호출 
       
        next_page = request.args.get('next') 
        # URL이 상대적인지 절대적인지 확인하기 위해 werkzeug의 url_parse() 함수로 구문 분석한 다음 net loc 구성요소가 설정되었는지 확인 (애플리케이션 보안을 강화하기 위함)
        if not next_page or url_parse(next_page).netloc != '': 
            next_page = url_for('index')    # 로그인 URL에 next 인수가 없으면 사용자는 인덱스 페이지로 리디렉션 
        return redirect(next_page)  # redirect() - 클라이언트 웹 브라우저가 인수로 지정된 다른 페이지로 자동으로 이동하도록 지시. 사용자를 애플리케이션의 색인 페이지로 리디렉션함.
    return render_template('login.html',  title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index')) # url_for('index') : index 함수에 대한 url을 얻어냄.


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
@app.route('/user/<username>') # <변수명> : 동적 구성 요소 , 사용자 이름으로 쿼리를 사용하여 데이터베이스에서 사용자를 로드
@login_required                # URL을 통해 전달받은 <username> 값으로 로직을 탄다. 
def user(username):  # <username> 이랑 변수명 맞춰줘야됨.
    # username에 맞는 값 가져오기 시도하여 성공하면 결과 가지고, 실패하면 404 에러 페이지 출력 
    #   -> 사용자 이름이 데이터베이스에 존재하지 않으면 함수가 반환되지 않고 대신 404예외가 발생하기 때문에 쿼리가 사용자를 반환했는지 확인하지 않아도 됨.
    user = User.query.filter_by(username=username).first_or_404() 
                              #(db에있는 column= 변수명)
    """
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    """
    # 사용자 프로필 보기 기능의 페이지 매김
    page = request.args.get('page', 1, type=int) 
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page , app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
   # print(f'>>>>>>>>>>>>>    {posts.items}') # [<Post post6>, <Post post5>, <Post post4>, <Post post3>, <Post post2>]
    # app.config['POSTS_PER_PAGE'] 만큼 출력 
    #print('>>>>> {next_url} , {prev_url}' )

    # 팔로우or언팔로우 버튼을 렌더링하기 위해 EmptyForm 객체를 인스턴스화 하여 user.html 템플릿에 전달  
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form)  # 성공하면 user 변수를 user에 넣고, posts 변수를 posts에 넣어 user.html 열기

# 마지막 방문 시간 기록
@app.before_request # before_request 데코레이터는 뷰 함 수 바로 전에 실행할 데코 레이팅 된 함수를 등록 
                    #-> request 되기 전에, 즉 웹페이지가 view가 출력되기 전에 실행하려는 코드를 이곳에 삽입
def before_request():
    # current_user가 로그인 되어있는지 확인하고 last_seen 필드를 현재 시간으로 설정 
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        # 커미하기 전 db.session.add()가 없는 이유? Flask-Login이 사용자 로더 콜백 함수를 호출하여 대상 사용자를 데이터베이스 세션에 넣는 데이터베이스 쿼리를 실행한다.


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    #form = EditProfileForm()
    form = EditProfileForm(current_user.username) # 프로필 편집 양식에서 사용자의 이름을 확인
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


# 경로를 따르고 팔로우, 언팔로우
# 다른 양식과 달리 자체 페이지가 없으며 양식은 user()경로에 의해 렌더링 되며 사용자의 프로필 페이지에 나타남. (user 경로에 EmptyForm 객체 인스턴스화 )
# 제출 부분만 구현하면 되므로 간단한 양식임 
@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username): # <username> 과 변수명 일치 
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
                                  #(db에있는 column= 변수명)
        if user is None:
            flash(f'User {username} not found')
            return redirect(url_for('index'))
        if user == current_user: # 현재 유저 본인이라면
            flash('You cannot follow yourself!')
        current_user.follow(user) 
        db.session.commit()
        flash(f'You are followung {username}!')
        return redirect(url_for('user', username=username)) 
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user',username=username))
        current_user.unfollow(user) 
        db.session.commit()
        flash(f'You are not followinng {username}')
    else:   # validate_on_submit() 호출이 실패 할 수 있는 유일한 이유는 CSRF 토큰이 없거나 유효하지 않은 경우
        return redirect(url_for('index')) # 이 경우 애플리케이션을 홈페이지로 다시 리디렉션함

# 탐색보기 기능
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    # 다음 및 이전 페이지 링크 생성하기
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None 
        
    return render_template('index.html', title='Explore', posts = posts.items,
                                        next_url=next_url, prev_url=prev_url)
                        # 이 페이지는 메인페이지(index)와 유사하므로 템플릿 재사용 
                        # but, 메인페이지에서 사용한 게시글 작성 폼은 탐색페이지에서 필요하지 않으므로 , 템플릿 호출에 form 인수를 포함하지 않는다.



## 비밀번호 재설정 요청보기 기능.
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:  # 인증된 유저라면
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    user = User.query.filter_by(email=form.email.data).first()
    print(f'::::::::::::::/reset_password_request >>>>{form.email.data}')
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(f'/:::::::reset_password_request >>>> user : {user}')
        if user: # 존재하는 email이라면
            send_password_reset_email(user) 
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', 
                            title='Reset Password', form=form )


## 비밀번호 재설정 보기 기능.
@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token) # 토큰 확인 방법을 호출하여 사용자가 누구인지 확인하기
    if not user: # 토큰 사용 결과 인증 실패시 
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    print(f'!!!!!!%%%% reset_password %%%%!!!!!!!!!! {user}')
    if form.validate_on_submit():
        user.set_password(form.password.data) # 비밀번호 재설정
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
