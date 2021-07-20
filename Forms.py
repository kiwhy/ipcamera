from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from models import User

class UserCreateForm(FlaskForm):
    userid = StringField('userid', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(), EqualTo('password_2', '비밀번호가 일치하지 않습니다')])
    password_2 = PasswordField('repassword', validators=[DataRequired()])

class LoginForm(FlaskForm):
    class UserPassword(object):
        def __init__(self, message=None):
            self.message = message

        def __call__(self, form, field):
            userid = form['userid'].data
            password = field.data

            usertable = User.query.filter_by(userid=userid).first()
            if usertable.password != password:
                raise ValueError('비밀번호 틀림')

    userid = StringField('userid', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), UserPassword()])