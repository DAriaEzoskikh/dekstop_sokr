import sqlite3
ac_level = ["Публичная", "Общий доступ", "Приватная"]
try:
    #создаем таблички, если их нет
    connect = sqlite3.connect(r"db.db", check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS "users" ("id" INTEGER NOT NULL,"login" TEXT NOT NULL, "password" TEXT NOT NULL, primary key("id" AUTOINCREMENT));''')
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS "accesses" ("id" INTEGER NOT NULL,"level" TEXT NOT NULL, primary key("id" AUTOINCREMENT));''')
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS "links" (
        "id" INTEGER NOT NULL, 
        "long" TEXT NOT NULL, 
        "short" TEXT NOT NULL, 
        "count" INTEGER NOT NULL, 
        "owner" INTEGER NOT NULL, 
        "access" INTEGER NOT NULL,
        primary key("id" AUTOINCREMENT),
        FOREIGN KEY ("owner") REFERENCES users("id"),
        FOREIGN KEY ("access") REFERENCES accesses("id")
        );''')

    #функция для категорий
    def count_category(cursor):
        categ = cursor.execute('''SELECT COUNT(*) FROM accesses;''').fetchone()
        return categ[0]
    k = 0
    if count_category(cursor) < 3:
        while k < 3:
            cursor.execute('''INSERT INTO accesses(level) VALUES (?);''', (ac_level[k],))
            k += 1

    connect.commit()

    #функция для поиска пользователя
    def find_user(cursor, login, passwod=False):




