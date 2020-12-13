from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from app.models import User

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