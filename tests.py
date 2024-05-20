import sqlite3


with sqlite3.connect('database.sqlite') as conn:
    c = conn.cursor()

    c.execute('SELECT * FROM rsvps')
    rows = c.fetchall()

    for row in rows:
        print(f'User: {row[0]}  Event: {row[1]}')

