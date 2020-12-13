from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm
from app.models import User, Post
from app.translate import translate
from app.main import bp



# 마지막 방문 시간 기록
@bp.before_request # before_request 데코레이터는 뷰 함 수 바로 전에 실행할 데코 레이팅 된 함수를 등록 
                    #-> request 되기 전에, 즉 웹페이지가 view가 출력되기 전에 실행하려는 코드를 이곳에 삽입
def before_request():
    # current_user가 로그인 되어있는지 확인하고 last_seen 필드를 현재 시간으로 설정 
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        # 커미하기 전 db.session.add()가 없는 이유? Flask-Login이 사용자 로더 콜백 함수를 호출하여 대상 사용자를 데이터베이스 세션에 넣는 데이터베이스 쿼리를 실행한다.
    g.locale = str(get_locale())




## route - uri를 정리해주는 것 
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required # Flask-Login이 익명 사용자로부터 뷰 기능을 데코레이터로 보호.
                # @bp.route 아래에 있는 뷰 함수에 추가하면 함수가 보호되고(/index 접근 유저는 인증된 유저여야만 함.), 인증되지 않은 사용자에게 액세스를 허용X 로그인이 필요한 페이지로 설정.
def index():
    form = PostForm()   # 게시글 작성하기 폼
    if form.validate_on_submit():
        #새 게시물의 언어를 저장
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        # 언어가 알려지지 않은 상태로 돌아오거나 예기치 않게 긴 결과가 나오면 안전하게 재생하고 빈 문자열을 데이터베이스에 저장.
        # 언어가 빈 문자열로 설정된 게시물은 알 수 없는 언어로 간주된다는 규칙을 채택

        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
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
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
     # view 함수의 next_url 및 prev_url은 (Flask-SQLAlchemy의 Pagination 클래스 객체에 있음)
     # 해당 방향에 페이지가 있는 경우에만 url_for()에서 반환하는 URL로 설정.
                
    return render_template('index.html', title='Home Page', form=form, posts=posts.items, 
                                                            next_url=next_url, prev_url=prev_url)
        # 렌더링 - 템플릿을 완전한 HTML 페이지로 변환하는 작업 
        # render_template() - {{ ... }} 블록을 render_template() 호출에 제공된 인수로 해당 값 대체
        #                   - 첫 번째 아규먼트로 렌더링 할 html 파일명을 넘겨주고, 그 이후에는 html 파일에 전달한 변수를 넘겨줌 

    




# 사용자 프로필보기 기능  
@bp.route('/user/<username>') # <변수명> : 동적 구성 요소 , 사용자 이름으로 쿼리를 사용하여 데이터베이스에서 사용자를 로드
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
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
   # print(f'>>>>>>>>>>>>>    {posts.items}') # [<Post post6>, <Post post5>, <Post post4>, <Post post3>, <Post post2>]
    # app.config['POSTS_PER_PAGE'] 만큼 출력 
    #print('>>>>> {next_url} , {prev_url}' )

    # 팔로우or언팔로우 버튼을 렌더링하기 위해 EmptyForm 객체를 인스턴스화 하여 user.html 템플릿에 전달  
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form)  # 성공하면 user 변수를 user에 넣고, posts 변수를 posts에 넣어 user.html 열기


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    #form = EditProfileForm()
    form = EditProfileForm(current_user.username) # 프로필 편집 양식에서 사용자의 이름을 확인
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


# 경로를 따르고 팔로우, 언팔로우
# 다른 양식과 달리 자체 페이지가 없으며 양식은 user()경로에 의해 렌더링 되며 사용자의 프로필 페이지에 나타남. (user 경로에 EmptyForm 객체 인스턴스화 )
# 제출 부분만 구현하면 되므로 간단한 양식임 
@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username): # <username> 과 변수명 일치 
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
                                  #(db에있는 column= 변수명)
        if user is None:
            flash(f'User {username} not found')
            return redirect(url_for('main.index'))
        if user == current_user: # 현재 유저 본인이라면
            flash('You cannot follow yourself!')
        current_user.follow(user) 
        db.session.commit()
        flash(f'You are followung {username}!')
        return redirect(url_for('main.user', username=username)) 
    else:
        return redirect(url_for('main.index'))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.user',username=username))
        current_user.unfollow(user) 
        db.session.commit()
        flash(f'You are not followinng {username}')
    else:   # validate_on_submit() 호출이 실패 할 수 있는 유일한 이유는 CSRF 토큰이 없거나 유효하지 않은 경우
        return redirect(url_for('main.index')) # 이 경우 애플리케이션을 홈페이지로 다시 리디렉션함

# 탐색보기 기능
@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    # 다음 및 이전 페이지 링크 생성하기
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None 
        
    return render_template('index.html', title='Explore', posts = posts.items,
                                        next_url=next_url, prev_url=prev_url)
                        # 이 페이지는 메인페이지(index)와 유사하므로 템플릿 재사용 
                        # but, 메인페이지에서 사용한 게시글 작성 폼은 탐색페이지에서 필요하지 않으므로 , 템플릿 호출에 form 인수를 포함하지 않는다.



## 텍스트 번역보기 기능
@bp.route('/translate',methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text':translate(request.form['text'],
                                     request.form['source_language'],
                                     request.form['dest_language'])})
    # request.form 속성은 플라스크가 제출에 포함한 모든 데이터를 노출하는 사전이다. 
    # 웹 양식으로 작업할 때 Flask-WTF가 모든 작업을 수행하기 때문에 request.form을 볼 필요가 없었지만,
    #  이 경우에는 실제로 웹 양식이 없으므로 데이터에 직접 액세스해야함. 
    #   -> translate() 함수를 호출하여 요청과 함께 제출된 데이터에서 직접 세 개의 인수를 전달
    # jsonify()의 반환 값은 클라이언트로 다시 전송 될 HTTP 응답
    