import psycopg2
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors

def connect_db():
    conn = psycopg2.connect(
        host='localhost',
        database='lab10',
        user='postgres',
        password='221756',
        port='5432'
    )
    return conn

conn = connect_db()
cur = conn.cursor()
query = "select * from genre where name = 'Rocka'"
try:
    cur.execute(query)
    conn.commit()
    rows = cur.fetchall()
    print(rows)
except errors.lookup(UNIQUE_VIOLATION):
    print("Genre already exists")

cur.close()
conn.close()

