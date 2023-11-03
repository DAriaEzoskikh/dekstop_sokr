import sqlite3
from flask import Flask, render_template, request, session
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, jwt_required
import db
import random
import hashlib

app = Flask(__name__, template_folder='templates', static_folder='templates/static')
app.config['SECRET_KEY']='123123123123123123123123123123123'
app.config["JWT_SECRET_KEY"]="youshallnotpass"
header = [{"name": "Главная", "url": "/"}, {"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "reg"}]

@app.route('/insert', methods=['POST'])
#создание пользователя
def insert():
    connect = sqlite3.connect('db.db', check_same_thread=False)
    cursor = connect.cursor()
    login = cursor.execute('''SELECT * from users where login = ? ''', (request.form['login'], )).fetchall()
    print(login)
    if login!=[]:
        return 'Такой логин уже есть, введите другой'
    else:
        hash = hashlib.md5(request.form['pass'].encode())
        password = hash.hexdigest()
        cursor.execute('''INSERT INTO users('login', 'password') VALUES(?, ?)''', (request.form['login'], password))
        connect.commit()
        user = cursor.execute('''SELECT * from users where login = ? ''', (request.form['login'],)).fetchone()

        session['user_id']  = user[0]
        session['user_login'] = user[1]
        if 'user_login' in session and session['user_login'] != None:
            header = [{"name": "Главная", "url": "/"},{"name": session['user_login'], "url": "profile"},]
        else:
            header = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"}, {"name": "Регистрация", "url": "reg"}]
        return render_template('profile.html', title="Профиль", header=header)

@app.route('/check', methods=['POST'])
#проверяем пользователя
def check():
    connect = sqlite3.connect('db.db', check_same_thread=False)
    cursor = connect.cursor()
    user = cursor.execute('''SELECT * from users where login = ? ''', (request.form['login'],)).fetchone()
    hash = hashlib.md5(request.form['password'].encode())
    password = hash.hexdigest()
    if password==user[2]:
        session['user_id'] = user[0]
        session['user_login'] = user[1]
        if 'user_login' in session and session['user_login'] != None:
            header = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"},

            ]
        else:
            header = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "reg"}]
        return render_template('profile.html', title="Профиль", header=header)
    else:
        return ('Неправильно введен пароль')

@app.route("/auth")
#авторизация
def auth():
    return render_template('auth.html', title="Авторизация", header=header)

@app.route("/reg")
#регистрация
def reg():
    header = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"}, {"name": "Регистрация", "url": "reg"}]
    return render_template('reg.html', title="Регистрация", header=header)

@app.route("/profile")
def profile():
    header = [{"name": "Главная", "url": "/"}, {"name": 'Профиль', "url": "profile"},]
    return render_template('profile.html', title="Профиль", header=header)

@app.route("/")
def index():
    if 'user_login' in session and session['user_login'] != None:
        header = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"},]
    else:
        header = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "reg"}]
    return render_template('index.html', title="Главная", header=header)

@app.route('/logout', methods=['POST'])
#выход
def logout():
    session['user_id'] = None
    session['user_login'] = None
    return render_template('index.html', title="Главная", header=header)

if __name__=='__main__':
    app.run(debug=True)



