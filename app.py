import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from models import db
from models import User
from flask import session
from flask_wtf.csrf import CSRFProtect
from Forms import UserCreateForm, LoginForm
import pymysql

app = Flask(__name__)

@app.route('/')
def mainpage():
    userid = session.get('userid', None)
    log_db = pymysql.connect(
        user='root',
        password='test',
        host='192.168.3.19',
        database='eventlog',
        charset='utf8'
    )
    cursor = log_db.cursor()

    sql = 'select * from eventlogtbl'
    cursor.execute(sql)

    data_list = cursor.fetchall()
    # return render_template('index2.html', data_list=data_list)
    return render_template('main.html', userid=userid, data_list=data_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserCreateForm()
    if form.validate_on_submit():  # 내용 채우지 않은 항목이 있는지까지 체크
        usertable = User()
        usertable.userid = form.data.get('userid')
        usertable.email = form.data.get('email')
        usertable.password = form.data.get('password')

        db.session.add(usertable)  # DB저장
        db.session.commit()  # 변동사항 반영

        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print('{}가 로그인'.format(form.data.get('userid')))
        session['userid']=form.data.get('userid')
        return redirect('/')
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userid', None)
    return redirect('/')

if __name__ == "__main__":
    basedir = os.path.abspath(os.path.dirname(__file__))
    dbfile = os.path.join(basedir, 'db.sqlite')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY']='asdf'

    csrf = CSRFProtect()
    csrf.init_app(app)

    db.init_app(app)
    db.app = app
    db.create_all()

    app.run(host="192.168.3.19", port=5000, debug=True)