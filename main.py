import datetime

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


#######################################################################################################################
# ---------------------------------------------- Pruebas ------------------------------------------------------------ #
#######################################################################################################################
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/user/")
async def get_users() -> list[models.User]:
    conn = connect_db()
    cur = conn.cursor()
    query = 'SELECT * FROM "usuario"'
    cur.execute(query)
    rows = cur.fetchall()

    result = []
    for row in rows:
        result.append(
            models.User(dpi=row[0], rol=row[1], password=row[2])
        )

    cur.close()
    conn.close()
    return result


#######################################################################################################################
# ------------------------------------------- UserLogin.jsx --------------------------------------------------------- #
#######################################################################################################################
@app.post("/user/login/")
async def login_user(user: models.UserLogin) -> models.UserDetails | dict:
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
            return models.UserDetails(
                dpi=row[0],
                nombre=row[1],
                direccion=row[2],
                telefono=row[3],
                num_colegiado=row[4],
                especialidad=row[5]
                # unidad_de_salud=row[6]
            )


#######################################################################################################################
# ----------------------------------------------- Signin.jsx -------------------------------------------------------- #
#######################################################################################################################

@app.post("/user/signup/")
async def signup_user(user: models.UserSignIn) -> models.UserDetails | dict:
    conn = connect_db()
    cur = conn.cursor()
    query_usuario = f"INSERT INTO usuario VALUES ('{user.dpi}', '{user.rol}', '{user.password}')"
    query_medico = f"INSERT INTO medico VALUES ('{user.dpi}', '{user.nombre}', '{user.direccion}', '{user.telefono}', '{user.num_colegiado}', '{user.especialidad}')"
    query_trabaja = f"INSERT INTO trabaja VALUES ('{datetime.date.today()}', null, '{user.dpi}', '{user.unidad_de_salud}')"
    print(query_usuario)
    print(query_medico)
    print(query_trabaja)
    return {"message": "User created successfully"}


@app.get("/user/dpi/")
async def get_dpis() -> list[str]:
    conn = connect_db()
    cur = conn.cursor()
    query = 'SELECT dpi FROM usuario'
    cur.execute(query)
    rows = cur.fetchall()
    print(rows)
    result = []
    for row in rows:
        result.append(row[0])
    cur.close()
    conn.close()
    return result


@app.get("/healthcenter/")
async def get_healthcenters() -> list[str]:
    conn = connect_db()
    cur = conn.cursor()
    query = 'SELECT nombre FROM unidad_salud'
    cur.execute(query)
    rows = cur.fetchall()
    print(rows)
    result = []
    for row in rows:
        result.append(row[0])
    cur.close()
    conn.close()
    return result


#######################################################################################################################
# ----------------------------------------------- Record.jsx -------------------------------------------------------- #
#######################################################################################################################

@app.get("/record/")
async def get_records(id: models.RecordSearch) -> list[models.Record] | dict:
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
        result.append(
            models.Record(
                no_expediente=row[0],
                paciente_dpi=row[1],
                medico_encargado=row[2],
                enfermedad_id=row[3],
                examenes=row[4],
                diagnosticos=row[5],
                fecha_atencion=row[6],
                cirugias=row[7],
                status=row[8],
                unidad_salud_id=row[9]
            )
        )

    cur.close()
    conn.close()
    return result


#######################################################################################################################
# --------------------------------------------- Inventory.jsx ------------------------------------------------------- #
#######################################################################################################################

@app.get("/inventory/")
async def get_inventory(id_unidad: models.BodegaSearch) -> list[models.Bodega] | dict:
    conn = connect_db()
    cur = conn.cursor()
    query = f"SELECT * FROM bodega WHERE unidad_salud_id = '{id_unidad.id}'"
    cur.execute(query)
    rows = cur.fetchall()

    if rows is None or len(rows) == 0:
        cur.close()
        conn.close()
        return {"message": "No records found"}

    result = []
    for row in rows:
        result.append(
            models.Bodega(
                id=row[0],
                detalle=row[1],
                cantidad=row[2],
                expiracion=str(row[3]),
                unidad_salud_id=row[4]
            )
        )

    cur.close()
    conn.close()
    return result


@app.put("/inventory/")
async def update_inventory(inventory: models.InventoryUpdate) -> models.Bodega | dict:
    conn = connect_db()
    cur = conn.cursor()
    query = f"UPDATE bodega SET existencia = {inventory.existencia} WHERE id = {inventory.id}"
    try:
        cur.execute(query)
        conn.commit()

        cur.execute(f"SELECT * FROM bodega WHERE id = {inventory.id}")  # Registro actualizado
        row = cur.fetchone()

        cur.close()
        conn.close()

        return models.Bodega(
            id=row[0],
            detalle=row[1],
            cantidad=row[2],
            expiracion=row[3],
            unidad_de_salud_id=row[4]
        )
    except Exception as e:
        print(e)
        return {"message": "Error updating inventory"}


#######################################################################################################################
# ---------------------------------------------- Add Product.jsx ---------------------------------------------------- #
#######################################################################################################################

@app.post("/inventory/add/")
async def add_product(product: models.ProductAdd) -> models.Bodega | dict:
    conn = connect_db()
    cur = conn.cursor()
    user_auth = f"set my.app_user = '{product.id_user_auth}'"
    cur.execute(user_auth)
    query = f"INSERT INTO bodega (detalle, cantidad, expiracion, unidad_salud_id) VALUES ('{product.detalle}', {product.cantidad}, date {product.expiracion}, {product.unidad_salud_id})"
    try:
        cur.execute(query)
        conn.commit()

        query = f"SELECT * FROM bodega WHERE detalle = '{product.detalle}' and existencia = true and cantidad = {product.cantidad} and expiracion = date '{product.expiracion}' and unidad_salud_id = {product.unidad_salud_id} "
        print(query)
        cur.execute(query)
        row = cur.fetchone()

        cur.close()
        conn.close()

        return models.Bodega(
            id=row[0],
            detalle=row[1],
            cantidad=row[2],
            expiracion=str(row[3]),
            unidad_salud_id=row[4]
        )
    except Exception as e:
        print(e)
        return {"message": "Error adding product"}


#######################################################################################################################
# -------------------------------------------------- Account.jsx ---------------------------------------------------- #
#######################################################################################################################

@app.get("/account/")
async def get_account(id: models.AccountRequest) -> models.AccountDetails | dict:
    conn = connect_db()
    cur = conn.cursor()

    query = f"SELECT m.dpi, m.nombre, m.direccion, m.telefono, m.num_colegiado, m.especialidad, t.unidad_salud_id FROM medico m LEFT JOIN trabaja t ON m.dpi = t.medico_dpi WHERE t.fecha_entrada = (SELECT max(fecha_entrada) FROM trabaja WHERE medico_dpi = m.dpi) AND m.dpi = '{id.dpi}'"
    cur.execute(query)
    row = cur.fetchone()

    if row is None:
        cur.close()
        conn.close()
        return {"message": "No account found"}

    result = models.AccountDetails(
        dpi=row[0],
        nombre=row[1],
        direccion=row[2],
        telefono=row[3],
        num_colegiado=row[4],
        especialidad=row[5],
        unidad_salud_id=row[6],
    )

    cur.close()
    conn.close()
    return result


@app.get("/account/workHistory/")
async def get_work_history(id: models.AccountRequest) -> list[models.WorkHistory] | dict:
    conn = connect_db()
    cur = conn.cursor()
    query = f"SELECT * FROM trabaja WHERE medico_dpi = '{id.dpi}'"
    cur.execute(query)
    rows = cur.fetchall()

    if rows is None or len(rows) == 0:
        cur.close()
        conn.close()
        return {"message": "No records found"}

    result = []
    for row in rows:
        result.append(
            models.WorkHistory(
                medico_dpi=row[0],
                unidad_salud_id=row[1],
                fecha_entrada=row[2],
                fecha_salida=row[3]
            )
        )

    cur.close()
    conn.close()
    return result


@app.put("/account/workHistory/")
async def update_work_history(work_history: models.WorkHistoryUpdate) -> models.WorkHistory | dict:
    conn = connect_db()
    cur = conn.cursor()
    # ASUMIENDO QUE SOLO PUEDE HABER UN REGISTRO CON NULL EN FECHA_SALIDA A LA VEZ
    query = f"UPDATE trabaja SET fecha_salida = date {datetime.date.today()} where fecha_salida is null and medico_dpi = '{work_history.medico_dpi}'"
    try:
        cur.execute(query)
        conn.commit()

        query = f"INSERT INTO trabaja values (date '{datetime.date.today()}', null, '{work_history.medico_dpi}', {work_history.unidad_salud_id})"
        cur.execute(query)

        cur.execute(f"SELECT * FROM trabaja WHERE medico_dpi = '{work_history.medico_dpi}' and unidad_salud_id = {work_history.unidad_salud_id} and fecha_entrada = date '{datetime.date.today()}'")
        row = cur.fetchone()

        cur.close()
        conn.close()

        return models.WorkHistory(
            medico_dpi=row[0],
            unidad_salud_id=row[1],
            fecha_entrada=row[2],
            fecha_salida=row[3]
        )
    except Exception as e:
        print(e)
        return {"message": "Error updating work history"}


@app.put("/account/")
async def update_account(account: models.AccountUpdate) -> models.UserDetails | dict:
    conn = connect_db()
    cur = conn.cursor()
    query = f"UPDATE medico SET direccion = '{account.direccion}', telefono = '{account.telefono}', especialidad = '{account.especialidad}' WHERE dpi = '{account.dpi}'"
    try:
        cur.execute(query)
        conn.commit()

        cur.execute(f"SELECT * FROM medico WHERE dpi = '{account.dpi}'")
        row = cur.fetchone()

        cur.close()
        conn.close()

        return models.UserDetails(
            dpi=row[0],
            nombre=row[1],
            direccion=row[2],
            telefono=row[3],
            num_colegiado=row[4],
            especialidad=row[5],
        )
    except Exception as e:
        print(e)
        return {"message": "Error updating account"}


#######################################################################################################################
# ---------------------------------------------- AddRecord.jsx ------------------------------------------------------ #
#######################################################################################################################
@app.get("/inventory/medicines")
async def get_medicines(id: models.MedicineSearch) -> list[models.MedicineResponse] | dict:
    conn = connect_db()
    cur = conn.cursor()

    id_unidad_query = f"SELECT id FROM unidad_salud WHERE nombre = '{id.unidad_salud}'"
    cur.execute(id_unidad_query)
    id_unidad = cur.fetchone()[0]
    print(id_unidad)

    query = f"SELECT b.id, b.detalle FROM bodega b WHERE b.unidad_salud_id = {id_unidad}"
    cur.execute(query)
    rows = cur.fetchall()

    if rows is None or len(rows) == 0:
        cur.close()
        conn.close()
        return {"message": "No records found"}

    result = []
    for row in rows:
        result.append(
            models.MedicineResponse(
                id=row[0],
                detalle=row[1]
            )
        )

    cur.close()
    conn.close()
    return result