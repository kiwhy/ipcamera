import os
from flask import Flask, render_template, redirect, Response
from models import db
from models import User
from flask import session
from flask_wtf.csrf import CSRFProtect
from Forms import UserCreateForm, LoginForm
import pymysql
import socket

UDP_IP = "192.168.50.190"
UDP_PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

app = Flask(__name__)

s = [b'\xff' * 46080 for x in range(20)]

@app.route('/')
def mainpage():
    userid = session.get('userid', None)
    log_db = pymysql.connect(
        user='root2',
        password='test',
        host='192.168.50.190',
        database='eventlog',
        charset='utf8'
    )
    cursor = log_db.cursor()

    sql = 'select * from eventlogtbl'
    cursor.execute(sql)

    data_list = cursor.fetchall()
    return render_template('index2.html', data_list=data_list)
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

@app.route('/streaming', methods=['GET'])
def index():
    return render_template('streaming.html')

def streaming():
    while True:
        picture = b''

        data, addr = sock.recvfrom(46081)
        s[data[0]] = data[1:46081]

        if data[0] == 19:
            for i in range(20):
                picture += s[i]

            frame = picture
            # frame = frame.reshape(640, 480, 3)
            # frame = frame.tobytes()

            yield (b'--frame\r\n'
                   b'content-type: image/jpg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(streaming(), mimetype='multipart/x-mixed-replace; boundary=frame')

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

    app.run(host="0.0.0.0", port=8080)