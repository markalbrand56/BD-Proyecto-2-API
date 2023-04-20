import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors
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
async def login_user(user: models.UserLogin) -> models.UserSuccessLogin | dict:
    conn = connect_db()
    cur = conn.cursor()
    query = f"SELECT * FROM usuario WHERE dpi = '{user.dpi}' AND contrasena = '{user.password}'"
    cur.execute(query)
    row = cur.fetchone()

    if row is None:
        cur.close()
        conn.close()
        return {
            "logged": False,
            "message": "Invalid username or password"
        }
    else:
        query = f"SELECT rol FROM usuario WHERE dpi = '{user.dpi}'"
        cur.execute(query)
        row = cur.fetchone()
        if row is None:
            cur.close()
            conn.close()
            return {
                "logged": False,
                "message": "Invalid username or password"
            }
        else:
            cur.close()
            conn.close()
            return {
                "logged": True,
                "user": models.UserSuccessLogin(
                    dpi=user.dpi,
                    rol=row[0]
                )
            }


#######################################################################################################################
# ----------------------------------------------- Signin.jsx -------------------------------------------------------- #
#######################################################################################################################

@app.post("/user/signup/")
async def sign_up_user_medico(user: models.UserSignIn) -> models.UserDetails | dict:
    conn = connect_db()
    cur = conn.cursor()

    query_auth = f"set my.app_user = '{user.dpi}'"
    cur.execute(query_auth)

    query = f"SELECT id FROM unidad_salud WHERE nombre = '{user.unidad_de_salud_nombre}'"
    cur.execute(query)
    unidad_salud_id = cur.fetchone()[0]
    query_usuario = f"INSERT INTO usuario VALUES ('{user.dpi}', '{user.rol}', '{user.password}')"
    query_medico = f"INSERT INTO medico VALUES ('{user.dpi}', '{user.nombre}', '{user.direccion}', '{user.telefono}', '{user.num_colegiado}', '{user.especialidad}')"
    query_trabaja = f"INSERT INTO trabaja VALUES ('{datetime.date.today()}', null, '{user.dpi}', '{unidad_salud_id}')"

    # print(query_usuario)
    # print(query_medico)
    # print(query_trabaja)

    try:
        cur.execute(query_usuario)
        conn.commit()
    except Exception as e:
        cur.close()
        conn.close()
        return {
            "created": False,
            "query": query_usuario,
            "user": None,
        }
    try:
        cur.execute(query_medico)
        conn.commit()
    except Exception as e:
        cur.close()
        conn.close()
        return {
            "created": False,
            "query": query_medico,
            "user": None,
        }

    try:
        cur.execute(query_trabaja)
        conn.commit()
    except Exception as e:
        cur.close()
        conn.close()
        return {
            "created": False,
            "query": query_trabaja,
            "user": None,
        }

    return {
        "created": True,
        "user": models.UserDetails(
            dpi=user.dpi,
            nombre=user.nombre,
            direccion=user.direccion,
            telefono=user.telefono,
            num_colegiado=user.num_colegiado,
            especialidad=user.especialidad
        )
    }


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
    result = []
    for row in rows:
        result.append(row[0])
    cur.close()
    conn.close()
    return result


@app.get("/healthcenter/{id}")
async def get_healthcenter_by_id(id: str) -> models.HealthCenter | dict:
    conn = connect_db()
    cur = conn.cursor()
    try:
        id = int(id)
    except Exception as e:
        return {
            "found": False,
            "message": "Invalid id"
        }
    query = f'SELECT * FROM unidad_salud WHERE id = {id}'
    print(query)

    cur.execute(query)
    row = cur.fetchone()

    if row is None:
        cur.close()
        conn.close()
        return {
            "found": False,
            "message": "Health center not found"
        }

    result = models.HealthCenter(
        id=row[0],
        tipo=row[1],
        nombre=row[2],
        direccion=row[3],
    )
    cur.close()
    conn.close()
    return {
        "found": True,
        "healthcenter": result
    }


@app.post("/healthcenter/getByName/")
async def get_healthcenter_by_name(healthcenter: models.HealthCenterName) -> models.HealthCenter | dict:
    conn = connect_db()
    cur = conn.cursor()
    query = f"SELECT * FROM unidad_salud WHERE nombre = '{healthcenter.nombre}'"
    print(query)

    cur.execute(query)
    row = cur.fetchone()

    if row is None:
        cur.close()
        conn.close()
        return {
            "found": False,
            "message": "Health center not found"
        }

    result = models.HealthCenter(
        id=row[0],
        tipo=row[1],
        nombre=row[2],
        direccion=row[3],
    )
    cur.close()
    conn.close()
    return {
        "found": True,
        "healthcenter": result
    }


#######################################################################################################################
# ----------------------------------------------- Record.jsx -------------------------------------------------------- #
#######################################################################################################################

@app.get("/record/{dpi}")
async def get_records_by_dpi(dpi: str) -> list[models.Record] | dict:
    conn = connect_db()
    cur = conn.cursor()
    query = f"SELECT * FROM expediente WHERE paciente_dpi = '{dpi}'"
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
                fecha_atencion=str(row[6]),
                cirugias=row[7],
                status=row[8],
                unidad_salud_id=row[9]
            )
        )

    cur.close()
    conn.close()
    return result


@app.post("/record/")
async def create_record(record: models.NewRecord) -> dict:
    conn = connect_db()
    cur = conn.cursor()

    query_auth = f"set my.app_user = '{record.dpi_auth}'"
    cur.execute(query_auth)

    id_expediente = None
    query = f"INSERT INTO expediente (paciente_dpi, medico_encargado, fecha_ingreso, status) VALUES ('{record.paciente_dpi}', '{record.medico_encargado}', '{record.fecha_atencion}', '{record.status}') RETURNING no_expediente"
    try:
        cur.execute(query)
        id_expediente = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        print(e)
        cur.close()
        conn.close()
        return {
            "added": False,
            "message": "Error al crear el expediente",
            "query": query
        }

    if record.enfermedad is not None:
        query = f"UPDATE expediente SET nombre_enfermedad = '{record.enfermedad}' WHERE no_expediente = {id_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "added": False,
                "message": "Error al añadir la enfermedad al expediente",
                "query": query
            }

    if record.evolucion is not None:
        query = f"UPDATE expediente SET evolucion = '{record.evolucion}' WHERE no_expediente = {id_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "added": False,
                "message": "Error al añadir la evolución al expediente",
                "query": query
            }

    if record.examenes is not None:
        query = f"UPDATE expediente SET examenes = '{record.examenes}' WHERE no_expediente = {id_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "added": False,
                "message": "Error al añadir los exámenes al expediente",
                "query": query
            }
    if record.diagnosticos is not None:
        query = f"UPDATE expediente SET diagnosticos = '{record.diagnosticos}' WHERE no_expediente = {id_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "added": False,
                "message": "Error al añadir los diagnósticos al expediente",
                "query": query
            }
    if record.fecha_salida is not None:
        query = f"UPDATE expediente SET fecha_salida = date '{record.fecha_salida}' WHERE no_expediente = {id_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "added": False,
                "message": "Error al añadir la fecha de salida al expediente",
                "query": query
            }
    if record.cirugias is not None:
        query = f"UPDATE expediente SET cirugias = '{record.cirugias}' WHERE no_expediente = {id_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "added": False,
                "message": "Error al añadir las cirugías al expediente",
                "query": query
            }

    if record.medicamentos is not None:
        for medicamento in record.medicamentos:
            query = f"INSERT INTO medicamentos VALUES ({id_expediente}, {medicamento}, 1)"
            try:
                cur.execute(query)
                conn.commit()
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return {
                    "added": False,
                    "message": "Error al añadir el medicamento al expediente",
                    "query": query
                }

    return {
        "added": True,
    }


#######################################################################################################################
# --------------------------------------------- Inventory.jsx ------------------------------------------------------- #
#######################################################################################################################

@app.post("/inventory/")
async def get_inventory_by_bodega_id(nombre_unidad: models.BodegaSearch) -> list[models.Bodega] | None:
    conn = connect_db()
    cur = conn.cursor()

    query = f"SELECT id FROM unidad_salud WHERE nombre = '{nombre_unidad.nombre_unidad_salud}'"
    try:
        cur.execute(query)
        id_unidad = cur.fetchone()[0]
    except Exception as e:
        cur.close()
        conn.close()
        return None

    query = f"SELECT * FROM bodega WHERE unidad_salud_id = '{id_unidad}'"
    cur.execute(query)
    rows = cur.fetchall()

    if rows is None or len(rows) == 0:
        cur.close()
        conn.close()
        return None

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
async def update_product_from_inventory(inventory: models.InventoryUpdate) -> models.Bodega | dict:
    conn = connect_db()
    cur = conn.cursor()

    query_auth = f"set my.app_user = '{inventory.dpi_auth}'"
    cur.execute(query_auth)

    query = f"UPDATE bodega SET cantidad = {inventory.existencia} WHERE id = {inventory.id}"
    try:
        cur.execute(query)
        conn.commit()

        cur.execute(f"SELECT * FROM bodega WHERE id = {inventory.id}")  # Registro actualizado
        row = cur.fetchone()

        cur.close()
        conn.close()

        return {
            "updated": True,
            "inventory": models.Bodega(
                id=row[0],
                detalle=row[1],
                cantidad=row[2],
                expiracion=str(row[3]),
                unidad_salud_id=row[4]
            )
        }
    except Exception as e:
        print(e)
        return {
            "updated": False,
            "message": "Error updating inventory"
        }


@app.get("/inventory/expired/{id_unidad_salud}")
async def get_expired_products(id_unidad_salud: int) -> list[models.BodegaMedicinasVencidas] | dict:
    conn = connect_db()
    cur = conn.cursor()

    query = f"SELECT b.id, b.unidad_salud_id, b.detalle, sum(b.cantidad) as cantidad_en_bodega FROM bodega b WHERE expiracion - current_date < 0 AND b.unidad_salud_id = {id_unidad_salud} GROUP BY b.detalle, b.unidad_salud_id, b.id"
    try:
        cur.execute(query)
        rows = cur.fetchall()
        result = []
        for row in rows:
            result.append(
                models.BodegaMedicinasVencidas(
                    id_en_bodega=row[0],
                    unidad_salud_id=row[1],
                    detalle=row[2],
                    cantidad=row[3]
                )
            )
        cur.close()
        conn.close()
        return {
            "executed": True,
            "expired_products": result
        }
    except Exception as e:
        print(e)
        return {
            "executed": False,
            "message": "Error updating inventory",
            "query": query
        }


#######################################################################################################################
# ---------------------------------------------- Add Product.jsx ---------------------------------------------------- #
#######################################################################################################################

@app.post("/inventory/add/")
async def add_new_product(product: models.ProductAdd) -> models.Bodega | dict:
    conn = connect_db()
    cur = conn.cursor()
    user_auth = f"set my.app_user = '{product.id_user_auth}'"
    cur.execute(user_auth)

    # Si trae cantidad mínima, se agrega a requisito_minimo
    if product.cantidad_minima is not None:
        try:
            query = f"INSERT INTO requisito_minimo VALUES ('{product.detalle}', {product.cantidad_minima}, {product.unidad_salud_id})"
            cur.execute(query)
            conn.commit()
        except errors.lookup(UNIQUE_VIOLATION) as e:
            conn.rollback()
            pass
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "added": False,
                "message": "Error adding product to requsito_minimo"
            }

    try:
        user_auth = f"set my.app_user = '{product.id_user_auth}'"
        cur.execute(user_auth)
        if product.expiracion is None:
            query = f"INSERT INTO bodega (detalle, cantidad, unidad_salud_id) VALUES ('{product.detalle}', {product.cantidad}, {product.unidad_salud_id})"
        else:
            query = f"INSERT INTO bodega (detalle, cantidad, expiracion, unidad_salud_id) VALUES ('{product.detalle}', {product.cantidad}, date '{product.expiracion}', {product.unidad_salud_id})"

        cur.execute(query)
        conn.commit()

        cur.close()
        conn.close()

        return {
            "added": True,
        }
    except Exception as e:
        print("ERROR: " + str(e))
        cur.close()
        conn.close()
        return {
            "added": False,
            "message": "Error adding product to bodega",
            "query": query
        }


#######################################################################################################################
# -------------------------------------------------- MyAccount.jsx -------------------------------------------------- #
#######################################################################################################################

@app.post("/account/")
async def get_account_by_dpi(id: models.AccountRequest) -> models.AccountDetails | dict:
    conn = connect_db()
    cur = conn.cursor()

    query = f"SELECT m.dpi, m.nombre, m.direccion, m.telefono, m.num_colegiado, m.especialidad, t.unidad_salud_id FROM medico m LEFT JOIN trabaja t ON m.dpi = t.medico_dpi WHERE t.fecha_entrada = (SELECT max(fecha_entrada) FROM trabaja WHERE medico_dpi = m.dpi) AND m.dpi = '{id.dpi}' AND t.fecha_salida is null"
    cur.execute(query)
    row = cur.fetchone()

    if row is None:
        cur.close()
        conn.close()
        return {
            "found": False,
            "message": "No records found"
        }

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
    return {
        "found": True,
        "account": result
    }


@app.post("/account/workHistory/")
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
                fecha_entrada=str(row[0]),
                fecha_salida=str(row[1]),
                medico_dpi=row[2],
                unidad_salud_id=row[3]
            )
        )

    cur.close()
    conn.close()
    return result


@app.put("/account/workHistory/")
async def update_work_history(work_history: models.WorkHistoryUpdate) -> models.WorkHistory | dict:
    conn = connect_db()
    cur = conn.cursor()

    query_auth = f"set my.app_user = '{work_history.dpi_auth}'"
    cur.execute(query_auth)

    # ASUMIENDO QUE SOLO PUEDE HABER UN REGISTRO CON NULL EN FECHA_SALIDA A LA VEZ
    query = f"UPDATE trabaja SET fecha_salida = date '{datetime.date.today()}' where fecha_salida is null and medico_dpi = '{work_history.medico_dpi}'"
    try:
        cur.execute(query)
        conn.commit()

        query = f"INSERT INTO trabaja values (date '{datetime.date.today()}', null, '{work_history.medico_dpi}', {work_history.unidad_salud_id})"
        print(f"Insert query: {query}")
        cur.execute(query)
        conn.commit()

        cur.execute(
            f"SELECT * FROM trabaja WHERE medico_dpi = '{work_history.medico_dpi}' and unidad_salud_id = {work_history.unidad_salud_id} and fecha_entrada = date '{datetime.date.today()}'")
        row = cur.fetchone()

        cur.close()
        conn.close()

        return models.WorkHistory(
            fecha_entrada=str(row[0]),
            fecha_salida=str(row[1]),
            medico_dpi=row[2],
            unidad_salud_id=row[3]
        )
    except Exception as e:
        print(e)
        return {"message": "Error updating work history"}


@app.put("/account/")
async def update_account(account: models.AccountUpdate) -> models.UserDetailsUpdate | dict:
    conn = connect_db()
    cur = conn.cursor()

    user_auth = f"set my.app_user = '{account.dpi}'"
    cur.execute(user_auth)

    query = f"UPDATE medico SET direccion = '{account.direccion}', telefono = '{account.telefono}', especialidad = '{account.especialidad}' WHERE dpi = '{account.dpi}'"
    try:
        cur.execute(query)
        conn.commit()

        cur.execute(f"SELECT * FROM medico WHERE dpi = '{account.dpi}'")
        row = cur.fetchone()

        query = f"SELECT unidad_salud_id FROM trabaja WHERE medico_dpi = '{account.dpi}' and fecha_salida is null"
        cur.execute(query)
        unidad_salud_id = cur.fetchone()[0]

        cur.close()
        conn.close()

        return {
            "updated": True,
            "account": models.UserDetailsUpdate(
                dpi=row[0],
                nombre=row[1],
                direccion=row[2],
                telefono=row[3],
                num_colegiado=row[4],
                especialidad=row[5],
                unidad_salud_id=unidad_salud_id
            )
        }
    except Exception as e:
        print(e)
        return {
            "updated": False,
            "message": "Error updating account"
        }


#######################################################################################################################
# ---------------------------------------------- AddRecord.jsx ------------------------------------------------------ #
#######################################################################################################################
@app.post("/inventory/medicines")
async def get_medicines_by_establecimiento(id: models.MedicineSearch) -> list[models.MedicineResponse] | dict:
    conn = connect_db()
    cur = conn.cursor()

    id_unidad_query = f"SELECT id FROM unidad_salud WHERE nombre = '{id.unidad_salud}'"
    cur.execute(id_unidad_query)
    row = cur.fetchone()
    if row is None:
        cur.close()
        conn.close()
        return {"message": "No unit found"}

    id_unidad = row[0]
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


#######################################################################################################################
# ---------------------------------------------- Binnacle.jsx ------------------------------------------------------- #
#######################################################################################################################
@app.get("/binnacle/")
async def get_binnacle() -> list[models.BinnacleResponse] | dict:
    conn = connect_db()
    cur = conn.cursor()
    query = f"SELECT * FROM bitacora"
    cur.execute(query)
    rows = cur.fetchall()

    if rows is None or len(rows) == 0:
        cur.close()
        conn.close()
        return {"message": "No records found"}

    result = []
    for row in rows:
        result.append(
            models.BinnacleResponse(
                accion=row[0],
                tabla=row[1],
                fecha=str(row[2]),
                usuario_dpi=row[3],
                usuario=row[4]
            )
        )

    cur.close()
    conn.close()
    return result


#######################################################################################################################
# ---------------------------------------------- Pacientes ---------------------------------------------------------- #
#######################################################################################################################

@app.get("/patients/{dpi}")
async def get_patient_by_dpi(dpi: str) -> models.PatientDetails | dict:
    conn = connect_db()
    cur = conn.cursor()

    query = f"SELECT * FROM paciente WHERE dpi = '{dpi}'"
    cur.execute(query)
    row = cur.fetchone()

    if row is None:
        cur.close()
        conn.close()
        return {
            "found": False,
            "patient": None,
            "message": "No patient found"
        }

    return {
        "found": True,
        "patient": models.PatientDetails(
            dpi=row[0],
            nombre=row[1],
            estatura=row[2],
            peso=row[3],
            telefono=row[4],
            adicciones=row[5],
            direccion=row[6],
            enfermedades_hereditarias=row[7]
        )
    }


@app.post("/patients/")
async def create_patient(patient: models.PatientCreate) -> models.PatientDetails | dict:
    conn = connect_db()
    cur = conn.cursor()

    query_auth = f"set my.app_user = '{patient.dpi_auth}'"
    cur.execute(query_auth)

    query = f"INSERT INTO paciente (dpi, nombre, estatura, peso, telefono, adicciones, direccion, enfermedades_hereditarias) VALUES ('{patient.dpi}', '{patient.nombre}', {patient.estatura}, {patient.peso}, '{patient.telefono}', '{patient.adicciones}', '{patient.direccion}', '{patient.enfermedades_hereditarias}')"
    try:
        cur.execute(query)
        conn.commit()

        cur.close()
        conn.close()

        return {
            "created": True,
        }
    except Exception as e:
        print(e)
        return {
            "created": False,
            "message": "Error creating patient",
            "query": query
        }


@app.put("/patients/")
async def update_patient_profile(patient: models.PatientUpdate) -> models.PatientDetails | dict:
    conn = connect_db()
    cur = conn.cursor()

    query_auth = f"set my.app_user = '{patient.dpi_auth}'"
    cur.execute(query_auth)

    query = f"UPDATE paciente SET estatura = {patient.estatura}, peso = {patient.peso}, telefono = '{patient.telefono}', adicciones = '{patient.adicciones}', direccion = '{patient.direccion}', enfermedades_hereditarias = '{patient.enfermedades_hereditarias}' WHERE dpi = '{patient.dpi}'"
    try:
        cur.execute(query)
        conn.commit()

        cur.close()
        conn.close()

        return {
            "updated": True,
        }
    except Exception as e:
        print(e)
        return {
            "updated": False,
            "message": "Error updating patient profile",
            "query": query
        }

# TODO LISTA DE MEDICINAS YA VENCIDAS
# TODO LISTA DE MEDICINAS POR VENCERSE EN EL PROXIMO MES
# TODO QUERY QUE REGRESE TODOS LOS MEDICAMENTOS DEBAJO DEL MÍNIMO
