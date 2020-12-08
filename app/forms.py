from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo , Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
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

    # 프로필 편집 양식에서 사용자 이름 확인
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Plaese use a diffrerent username.')
                # raise - 오류를 강제로 발생시키기 



