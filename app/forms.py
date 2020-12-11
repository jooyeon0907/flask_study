from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo , Length
from app.models import User
from flask_babel import lazy_gettext as _l

class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()]) # 이메일 주소의 구조와 일치하는지 확인하는 WTForms와 함께 제공되는 또 다른 주식 유효성 검사기
    password = PasswordField('Password', validators=[DataRequired()])
    # 비밀번호는 오타 방지를 위해 두 번 입력하도록 하고, 일치하는 지 확인
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')]) # EqualTo : 두 필드 값 비교(패스워드 검증)
    submit = SubmitField('Register')

    # 이미 있는 사용자명일 경우 사용 불가 
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please ise a diffrerent username.')
    
    # 이미 있는 이메일일 경우 사용 불가 
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    # 프로필 편집 양식에서 사용자 이름 확인 -> 데이터베이스에 입력한 이름이 존재하지 않는지 확인
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    

    def validate_username(self, username):
        if username.data != self.original_username: 
            # 사용자가 원래 사용자의 이름을 그대로 두면 이미 해당 사용자에게 할당되었으므로 
            # 유효성 검사에서 허용하므로 이름이 같지 않을때의 조건을 건다.
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Plaese use a diffrerent username.')
                # raise - 오류를 강제로 발생시키기 

# 팔로우 및 언 팔로우를 위한 빈 양식
class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')
 #  데이터 필드가 없이 작업을 수행하지만,sqlite3.OperationalError: no such table: user
 #  숨겨진 필드로 구현되고(@app.route('/user/<username>')에서)
 #  Flask-WTF에 의해 자동으로 추가되는 CSRF 토큰과 사용자가 작업을 트리거하기 위해 클릭해야하는 제출 버튼
 #  GET 요청으로 구현하면 CSRF 공격에서 악용 될 수 있음 (보호하기가 더 어려움)


# 사용자가 새 게시물을 입력할 수 있는 양식
class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('게시글올리기')

# 비밀번호 재설정 요청 양식
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

# 비밀번호 재설정 양식
class ResetPasswordForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')