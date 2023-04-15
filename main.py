import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
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

    result = []
    for row in rows:
        result.append({
            "dpi": row[0],
            "rol": row[1],
            "contrasena": row[2]
        })
    users = jsonable_encoder(result)

    cur.close()
    conn.close()
    return JSONResponse(content=users)


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
                "especialidad": row[5],
                "unidad_de_salud": None,  # CAMBIAR
            }


@app.post("/user/signup/")
async def signup_user(user: models.UserSignIn):
    conn = connect_db()
    cur = conn.cursor()
    query_usuario = f"INSERT INTO usuario VALUES ('{user.dpi}', '{user.rol}', '{user.password}')"
    query_medico = f"INSERT INTO medico VALUES ('{user.dpi}', '{user.nombre}', '{user.direccion}', '{user.telefono}', '{user.num_colegiado}', '{user.especialidad}')"
    query_trabaja = f"INSERT INTO trabaja VALUES ('{datetime.date.today()}', null, '{user.dpi}', '{user.unidad_de_salud}')"
    print(query_usuario)
    print(query_medico)
    print(query_trabaja)
    return {"message": "User created successfully"}


@app.get("/record/")
async def get_records(id: models.RecordSearch):
    conn = connect_db()
    cur = conn.cursor()
    query = f"SELECT * FROM expediente WHERE paciente_dpi = '{id.dpi}'"
    cur.execute(query)
    rows = cur.fetchall()

    if rows is None or len(rows) == 0:
        cur.close()
        conn.close()
        return {"message": "No records found"}

    result = []
    for row in rows:
        result.append({
            "no_expediente": row[0],
            "paciente_dpi": row[1],
            "medico_encargado": row[2],
            "enfermedad_id": row[3],
            "examenes": row[4],
            "diagnosticos": row[5],
            "fecha_atencion": row[6],
            "cirugias": row[7],
            "status": row[8],
            "unidad_salud_id": row[9]
        })

    expedientes = jsonable_encoder(result)
    cur.close()
    conn.close()
    return JSONResponse(content=expedientes)
