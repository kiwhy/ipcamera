from flask import Flask, render_template
import pymysql

app = Flask(__name__)


@app.route('/')
def index():
    log_db = pymysql.connect(
        user='root2',
        password='test',
        host='193.123.234.179',
        database='eventlog',
        charset='utf8'
    )
    cursor = log_db.cursor()

    sql = 'select * from eventlogtbl'
    cursor.execute(sql)

    data_list = cursor.fetchall()
    return render_template('index2.html', data_list=data_list)

if __name__ =='__main__':
    app.run()