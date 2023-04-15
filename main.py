from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import psycopg2
import models

app = FastAPI()
load_dotenv()


def connect_db():
    conn = psycopg2.connect(
        database='bdproyecto2',
        user=os.getenv('AWS_RDS_USR'),
        password=os.getenv('AWS_RDS_PWD'),
        host=os.getenv('AWS_RDS_HOST'),
        port=os.getenv('AWS_RDS_PORT')
    )
    return conn


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/user/")
async def get_users():
    conn = connect_db()
    cur = conn.cursor()
    query = 'SELECT * FROM "usuario"'
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/user/login/")
async def login_user(user: models.UserLogin):
    conn = connect_db()
    cur = conn.cursor()
    query = f"SELECT * FROM usuario WHERE dpi = '{user.dpi}' AND contrasena = '{user.password}'"
    cur.execute(query)
    row = cur.fetchone()

    if row is None:
        cur.close()
        conn.close()
        return {"message": "Invalid username or password"}
    else:
        query = f"SELECT * FROM medico WHERE dpi = '{user.dpi}'"
        cur.execute(query)
        row = cur.fetchone()
        if row is None:
            cur.close()
            conn.close()
            return {"message": "Invalid username or password"}
        else:
            cur.close()
            conn.close()
            return {
                "dpi": row[0],
                "nombre": row[1],
                "direccion": row[2],
                "telefono": row[3],
                "num_colegiado": row[4],
                "especialidad": row[5]
            }