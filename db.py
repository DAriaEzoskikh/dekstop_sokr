import sqlite3

connect = sqlite3.connect("db.db")
cursor = connect.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS  "users" (
	"id"	INTEGER,
	"login"	TEXT,
	"password"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
''')

cursor.execute('''
 CREATE TABLE IF NOT EXISTS "links_types" (
	"id"	INTEGER,
	"type"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
''')

# cursor.execute("""delete from links""")

cursor.execute('''
 CREATE TABLE IF NOT EXISTS "links" (
	"id"	INTEGER,
	"link"	TEXT,
	"hreflink"	TEXT,
	"user_id"	INTEGER,
	"link_type_id"	INTEGER,
	"count"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
    FOREIGN KEY (user_id)  REFERENCES users (id),
    FOREIGN KEY (link_type_id)  REFERENCES links_types (id)
);
''')
connect.commit()

links_types = cursor.execute('''select * from links_types''').fetchall()
if links_types==[]:
    cursor.execute('''insert into links_types (type) values('Публичная')''')
    connect.commit()
    cursor.execute('''insert into links_types (type) values('Общая')''')
    connect.commit()
    cursor.execute('''insert into links_types (type) values('Приватная')''')
    connect.commit()

