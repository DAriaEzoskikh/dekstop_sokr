import random
import hashlib
import db
import sqlite3
import flask
from flask import Flask, render_template, request, session, redirect
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, jwt_required

app = Flask(__name__, template_folder='templates', static_folder='templates/static')

jwt = JWTManager(app)

app.config['SECRET_KEY']='123123123123123123123123123123123'
app.config["JWT_SECRET_KEY"]="youshallnotpass"
header = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "reg"}
        ]

@app.route('/insert', methods=['POST'])
def insert():
    connect = sqlite3.connect('db.db', check_same_thread=False)
    cursor = connect.cursor()
    login = cursor.execute('''SELECT * from users where login = ? ''', (request.form['login'], )).fetchall()
    if login!=[]:
        return 'Логин занят'
    else:
        hash = hashlib.md5(request.form['pass'].encode())
        password = hash.hexdigest()
        cursor.execute('''INSERT INTO users('login', 'password') VALUES(?, ?)''', (request.form['login'], password))
        connect.commit()
        user = cursor.execute('''SELECT * from users where login = ? ''', (request.form['login'],)).fetchone()

        session['user_id']  = user[0]
        session['user_login'] = user[1]
        if 'user_login' in session and session['user_login'] != None:
            header = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"}]
        else:
            header = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "reg"}]
        return render_template('profile.html', title="Профиль", header=header)

@app.route('/check', methods=['POST'])
def check():
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    user = cursor.execute('''SELECT * FROM 'users' WHERE login = ?''', (request.form["login"],)).fetchone()
    hash = hashlib.md5(request.form["password"].encode())
    password = hash.hexdigest()
    header = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "reg"}]
    if user != None:
        if password == user[2]:
            session['user_login'] = user[1]
            session['user_id'] = user[0]
            hrefs = cursor.execute('''SELECT * FROM 'links' WHERE user_id = ?''', (session['user_id'],)).fetchall()
            header = [
                {"name": "Главная", "url": "/"},
                {"name": 'Профиль', "url": "profile"},
            ]
            if 'href' in session and session['href'] != None:
                if session['href'][6] == 2:
                    addres = session['href'][1]
                    href = cursor.execute(
                        '''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE links.id = ?''',
                        (session['href'][0],)).fetchone()
                    cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
                    connect.commit()
                    session['href'] = None
                    session['user_login'] = None
                    session['user_id'] = None
                    return redirect(f"{addres}")
                else:
                    if session['href'][3] == session['user_id']:
                        addres = session['href'][1]
                        href = cursor.execute(
                            '''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE links.id = ?''',
                            (session['href'][0],)).fetchone()
                        cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
                        connect.commit()
                        session['href'] = None
                        session['user_login'] = None
                        session['user_id'] = None
                        connect.commit()
                        return redirect(f"{addres}")
                    else:
                        session['href'] = None
                        session['user_login'] = None
                        session['user_id'] = None
                        return 'Нет доступа'
            else:
                hrefs = cursor.execute(
                    '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
                    (session['user_id'],)).fetchall()
                type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
                connect = sqlite3.connect('db.db', check_same_thread=False)
                cursor = connect.cursor()
                link_table = cursor.execute('''select * from links inner join links_types on links.link_type_id=links_types.id where user_id=?''',(session['user_id'],)).fetchall()
                return render_template('profile.html', title="Профиль", header=header, hrefs=hrefs, type=type, baselink=request.host_url, link_table=link_table)
        else:
            flask.flash('Неправильный пароль')
            return render_template('auth.html', title="Авторизация", header=header)
    else:
        flask.flash('Вас нет в базе')
        return render_template('auth.html', title="Авторизация", header=header)


@app.route("/")
def index():
    if 'user_login' in session and session['user_login'] != None:
        header = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"},]
    else:
        header = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "reg"}]
    return render_template('index.html', title="Главная", header=header)

@app.route('/logout', methods=['POST'])
def logout():
    session['user_id'] = None
    session['user_login'] = None
    return render_template('index.html', title="Главная", header=header)

@app.route("/auth")
def auth():
    return render_template('auth.html', title="Авторизация", header=header)

@app.route("/reg")
def reg():
    header = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "reg"}]
    return render_template('reg.html', title="Регистрация", header=header)

@app.route("/profile")
def profile():
    header = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"},]
    connect = sqlite3.connect('db.db', check_same_thread=False)
    cursor = connect.cursor()
    link_table = cursor.execute('''select * from links inner join links_types on links.link_type_id=links_types.id where user_id=?''',(session['user_id'],)).fetchall()
    return render_template('profile.html', title="Профиль", header=header, link_table=link_table, baselink=request.host_url)

@app.route("/reduce", methods=['POST'])
def short():
    if 'user_login' in session and session['user_login'] !=None:
        header = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"},]
    else:
        header = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "reg"}]
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    if request.form['psev']!='':
        psev = cursor.execute('''select * from links where hreflink=?''', (request.form['psev'], )).fetchone()
        if psev==None:
            user_address=request.form['psev']
        else:
            user_address = hashlib.md5(request.form['href'].encode()).hexdigest()[:random.randint(8, 12)]
    else:
        user_address = hashlib.md5(request.form['href'].encode()).hexdigest()[:random.randint(8, 12)]
    if request.form['link']=='1':
        if ('user_id' in session and session['user_id']!=None):
            cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['href'], user_address, session['user_id'], request.form['link'],0))
            connect.commit()
            baselink23 = request.host_url + 'href/' + user_address

            flask.flash(f'{baselink23}')
            return render_template('index.html', title="Главная", header=header, )
        else:
            cursor.execute('''INSERT INTO links('link', 'hreflink', 'link_type_id', 'count') VALUES(?, ?, ?, ?)''', (request.form['href'], user_address, request.form['link'], 0))
            connect.commit()
            baselink23 = request.host_url + 'href/' + user_address

            flask.flash(f'{baselink23}')
            return render_template('index.html', title="Главная", header=header, )

    elif request.form['link']=='2':
        cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['href'], user_address, session['user_id'], request.form['link'], 0))
        connect.commit()
        baselink23 = request.host_url + 'href/' + user_address

        flask.flash(f'{baselink23}')
        return render_template('index.html', title="Главная", header=header, )
    else:
        cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['href'], user_address, session['user_id'], request.form['link'], 0))
        connect.commit()
        baselink23 = request.host_url + 'href/' + user_address

        flask.flash(f'{baselink23}')
        return render_template('index.html', title="Главная", header=header, )


@app.route("/href/<hashref>")
def direct(hashref):
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    href = cursor.execute('''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE hreflink = ?''', (hashref, ) ).fetchone()
    if href[7]=='Публичная':
        cursor.execute('''UPDATE links SET count = ? WHERE id=?''',(href[5]+1, href[0]))
        connect.commit()
        return redirect(f"{href[1]}")
    elif href[7]=='Общая':
        if 'user_id' in session and session['user_id']!=None:
            cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
            connect.commit()
            return redirect(f"{href[1]}")
        else:
            session['href'] = href
            header = [{"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "reg"}]
            return render_template('avto.html', title="Авторизация", header=header)

    elif href[7]=='Приватня':
        if 'user_id' in session and session['user_id'] != None:
            if (href[3]==session['user_id']):
                cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
                connect.commit()
                return redirect(f"{href[1]}")
            else:
                return ('Нет доступа')
        else:
            session['href'] = href
            header = [{"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "reg"}]
            return render_template('auth.html', title="Авторизация", header=header)

@app.route("/delete", methods=['POST'])
def delete():
            connect = sqlite3.connect('db.db')
            cursor = connect.cursor()
            cursor.execute('''DELETE FROM 'links' WHERE id = ?''', (request.form['delete'],))
            connect.commit()
            header = [{"name": "Главная", "url": "/"},{"name": session['user_login'], "url": "profile"},]
            href = cursor.execute(
                '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
                (session['user_id'],)).fetchall()
            type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
            link_table = cursor.execute(
                '''select * from links inner join links_types on links.link_type_id=links_types.id where user_id=?''',
                (session['user_id'],)).fetchall()

            return render_template('profile.html', title="Профиль", header=header, href=href, type=type, baselink=request.host_url, link_table=link_table)

@app.route("/update", methods=['POST'])
def update():
    header = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"},]
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    href = cursor.execute('''select id, hreflink from links where id=?''', (request.form['update'], )).fetchone()
    return render_template('update.html', title="Изменение", header=header, href=href)

@app.route("/save", methods=['POST'])
def save():
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    header = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"},]
    if request.form['select']=='0':
        cursor.execute('''UPDATE links SET hreflink = ? WHERE id = ?''', (request.form["psev"],request.form["id"]))
        connect.commit()
    else:
        cursor.execute('''UPDATE links SET hreflink = ?, link_type_id=? WHERE id = ?''', (request.form["psev"],request.form["select"], request.form["id"]))
        connect.commit()
    href = cursor.execute('''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',(session['user_id'],)).fetchall()
    link_table = cursor.execute('''select * from links inner join links_types on links.link_type_id=links_types.id where user_id=?''',(session['user_id'],)).fetchall()
    return render_template('profile.html', title="Профиль", header=header, href=href, type=type, baselink=request.host_url, link_table=link_table)
if __name__=='__main__':
    app.run(debug=True)