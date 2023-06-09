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
        return {
            "found": False,
            "message": "No records found"
        }

    result = []
    for row in rows:
        new_record = models.Record(
            no_expediente=row[0],
            paciente_dpi=row[1],
            medico_encargado=row[2],
            fecha_atencion=str(row[5]),
            status=row[8],
            unidad_salud_id=row[9],
        )

        if row[3] is not None:
            new_record.examenes = row[3]

        if row[4] is not None:
            new_record.diagnosticos = row[4]

        if row[5] is not None:
            new_record.fecha_atencion = str(row[5])

        if row[6] is not None:
            new_record.fecha_salida = str(row[6])

        if row[7] is not None:
            new_record.cirugias = row[7]

        if row[10] is not None:
            new_record.enfermedad = row[10]

        if row[11] is not None:
            new_record.evolucion = row[11]

        result.append(new_record)

    cur.close()
    conn.close()
    return {
        "found": True,
        "records": result
    }


@app.post("/record/")
async def create_record(record: models.NewRecord) -> dict:
    conn = connect_db()
    cur = conn.cursor()

    query_auth = f"set my.app_user = '{record.dpi_auth}'"
    cur.execute(query_auth)

    # Verificar si el paciente existe
    query_ver = f"SELECT * FROM paciente WHERE dpi = '{record.paciente_dpi}'"
    cur.execute(query_ver)
    row = cur.fetchone()
    if row is None:
        cur.close()
        conn.close()
        return {
            "added": False,
            "message": "El paciente no existe"
        }

    # Verificar si el paciente ya falleció
    query_ver = f"SELECT * FROM expediente WHERE paciente_dpi = '{record.paciente_dpi}' AND status = 'Fallecido'"
    cur.execute(query_ver)
    row = cur.fetchone()
    if row is not None:
        cur.close()
        conn.close()
        return {
            "added": False,
            "message": "El paciente ya falleció"
        }

    id_expediente = None
    query = f"INSERT INTO expediente (paciente_dpi, medico_encargado, fecha_ingreso, status, unidad_salud_id) VALUES ('{record.paciente_dpi}', '{record.medico_encargado}', '{record.fecha_atencion}', '{record.status}', {record.unidad_salud_id}) RETURNING no_expediente"
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


@app.put("/record/")
async def update_record(record: models.UpdateRecord) -> dict:
    conn = connect_db()
    cur = conn.cursor()

    query_auth = f"set my.app_user = '{record.dpi_auth}'"
    cur.execute(query_auth)

    query_ver = f"SELECT * FROM expediente WHERE no_expediente = {record.no_expediente} and paciente_dpi = '{record.paciente_dpi}'"
    cur.execute(query_ver)
    row = cur.fetchone()

    if row is None:
        cur.close()
        conn.close()
        return {
            "updated": False,
            "message": "El expediente no existe"
        }

    if record.examenes is not None:
        query = f"UPDATE expediente SET examenes = '{record.examenes}' WHERE no_expediente = {record.no_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "updated": False,
                "message": "Error al actualizar los exámenes del expediente",
                "query": query
            }

    if record.diagnosticos is not None:
        query = f"UPDATE expediente SET diagnosticos = '{record.diagnosticos}' WHERE no_expediente = {record.no_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "updated": False,
                "message": "Error al actualizar los diagnósticos del expediente",
                "query": query
            }

    if record.fecha_salida is not None:
        query = f"UPDATE expediente SET fecha_salida = date '{record.fecha_salida}' WHERE no_expediente = {record.no_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "updated": False,
                "message": "Error al actualizar la fecha de salida del expediente",
                "query": query
            }

    if record.cirugias is not None:
        query = f"UPDATE expediente SET cirugias = '{record.cirugias}' WHERE no_expediente = {record.no_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "updated": False,
                "message": "Error al actualizar las cirugías del expediente",
                "query": query
            }

    if record.status is not None and row[8] != "Fallecido":  # Si está fallecido, no se puede revertir
        query = f"UPDATE expediente SET status = '{record.status}' WHERE no_expediente = {record.no_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "updated": False,
                "message": "Error al actualizar el status del expediente",
                "query": query
            }

    if record.enfermedad is not None:
        query = f"UPDATE expediente SET nombre_enfermedad = '{record.enfermedad}' WHERE no_expediente = {record.no_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "updated": False,
                "message": "Error al actualizar la enfermedad del expediente",
                "query": query
            }

    if record.evolucion is not None:
        query = f"UPDATE expediente SET evolucion = '{record.evolucion}' WHERE no_expediente = {record.no_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "updated": False,
                "message": "Error al actualizar la evolución del expediente",
                "query": query
            }

    if record.medico_encargado is not None:
        query = f"UPDATE expediente SET medico_encargado = '{record.medico_encargado}' WHERE no_expediente = {record.no_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "updated": False,
                "message": "Error al actualizar el médico encargado del expediente",
                "query": query
            }

    if record.fecha_atencion is not None:
        query = f"UPDATE expediente SET fecha_ingreso = date '{record.fecha_atencion}' WHERE no_expediente = {record.no_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "added": False,
                "message": "Error al actualizar la fecha de atención del expediente",
                "query": query
            }

    if record.unidad_salud_id is not None:
        query = f"UPDATE expediente SET unidad_salud_id = {record.unidad_salud_id} WHERE no_expediente = {record.no_expediente}"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return {
                "updated": False,
                "message": "Error al actualizar la unidad de salud del expediente",
                "query": query
            }

    if record.medicamentos is not None:
        for medicamento in record.medicamentos:

            query_ver = f"SELECT cantidad_utilizada FROM medicamentos WHERE expediente_numero = {record.no_expediente} AND bodega_id = {medicamento}"

            try:
                cur.execute(query_ver)
                row = cur.fetchone()
                if row is not None:
                    query = f"UPDATE medicamentos SET cantidad_utilizada = {row[0] + 1} WHERE expediente_numero = {record.no_expediente} AND bodega_id = {medicamento}"
                    try:
                        cur.execute(query)
                        conn.commit()
                    except Exception as e:
                        print(e)
                        cur.close()
                        conn.close()
                        return {
                            "updated": False,
                            "message": "Error al actualizar los medicamentos del expediente",
                            "query": query
                        }
                    continue
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return {
                    "updated": False,
                    "message": "Error al actualizar los medicamentos del expediente",
                    "query": query_ver
                }

            query = f"INSERT INTO medicamentos VALUES ({record.no_expediente}, {medicamento}, 1)"
            try:
                cur.execute(query)
                conn.commit()
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return {
                    "updated": False,
                    "message": "Error al actualizar los medicamentos del expediente",
                    "query": query
                }

    cur.close()
    conn.close()
    return {
        "updated": True,
        "message": "Expediente actualizado correctamente",
    }


@app.get("/record/medicine/{no_expediente}")
async def get_medicines_by_record(no_expediente: int) -> list[models.MedicinaExpediente] | dict:
    conn = connect_db()
    cur = conn.cursor()

    query = f"SELECT b.detalle, sum(m.cantidad_utilizada) as cantidad FROM medicamentos m INNER JOIN bodega b on b.id = m.bodega_id WHERE expediente_numero = {no_expediente} group by b.detalle"
    try:
        cur.execute(query)
        rows = cur.fetchall()

        result = []
        for row in rows:
            result.append(
                models.MedicinaExpediente(
                    medicamento=row[0],
                    cantidad=row[1]
                )
            )

        return {
            "found": True,
            "medicines": result,
        }
    except Exception as e:
        print(e)
        cur.close()
        conn.close()
        return {
            "found": False,
            "message": "Error al obtener los medicamentos del expediente",
            "query": query
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
        if row[3] is None:
            result.append(
                models.Bodega(
                    id=row[0],
                    detalle=row[1],
                    cantidad=row[2],
                    expiracion=None,
                    unidad_salud_id=row[4]
                )
            )
        else:
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


@app.get("/inventory/toExpire/{id_unidad_salud}")
async def get_products_to_expire(id_unidad_salud: int) -> list[models.BodegaMedicinasPorVencer] | dict:
    conn = connect_db()
    cur = conn.cursor()

    query = f"SELECT b.id, b.unidad_salud_id, b.detalle, b.expiracion, sum(b.cantidad) as cantidad_en_bodega FROM bodega b WHERE expiracion - current_date < 30 and expiracion - current_date > 0 and b.unidad_salud_id = {id_unidad_salud} GROUP BY b.id"
    try:
        cur.execute(query)
        rows = cur.fetchall()
        result = []
        for row in rows:
            result.append(
                models.BodegaMedicinasPorVencer(
                    id_en_bodega=row[0],
                    unidad_salud_id=row[1],
                    detalle=row[2],
                    fecha_expiracion=str(row[3]),
                    cantidad_en_bodega=row[4]
                )
            )
        cur.close()
        conn.close()
        return {
            "executed": True,
            "products_to_expire": result
        }
    except Exception as e:
        print(e)
        return {
            "executed": False,
            "products_to_expire": None,
            "message": "Error updating inventory",
            "query": query
        }


@app.get("/inventory/lowStock/{id_unidad_salud}")
async def get_products_low_stock(id_unidad_salud: int) -> list[models.MedicinasBajoStock] | dict:
    conn = connect_db()
    cur = conn.cursor()

    query = f"SELECT b.unidad_salud_id, b.detalle, rm.cantidad_minima, sum(b.cantidad) as cantidad_en_bodega FROM bodega b INNER JOIN requisito_minimo rm ON rm.detalle = b.detalle AND rm.unidad_salud_id = b.unidad_salud_id WHERE (b.expiracion - current_date > 30 OR b.expiracion is null) AND b.unidad_salud_id = {id_unidad_salud} GROUP BY b.unidad_salud_id, b.detalle, rm.cantidad_minima HAVING sum(b.cantidad) < rm.cantidad_minima"
    try:
        cur.execute(query)
        rows = cur.fetchall()
        result = []
        for row in rows:
            result.append(
                models.MedicinasBajoStock(
                    unidad_salud_id=row[0],
                    detalle=row[1],
                    cantidad_minima=row[2],
                    cantidad_en_bodega=row[3]
                )
            )
        cur.close()
        conn.close()
        return {
            "executed": True,
            "products_low_stock": result
        }
    except Exception as e:
        print(e)
        return {
            "executed": False,
            "products_low_stock": None,
            "message": "Error fetching inventory",
            "query": query
        }


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

    query = f"SELECT b.id, b.detalle, b.expiracion FROM bodega b WHERE b.unidad_salud_id = {id_unidad} and expiracion > current_date and b.cantidad > 0"
    cur.execute(query)
    rows = cur.fetchall()

    if rows is None or len(rows) == 0:
        cur.close()
        conn.close()
        return {"message": "No records found"}

    result = []
    for row in rows:
        med = models.MedicineResponse(
            id=row[0],
            detalle=row[1]
        )

        if row[2] is not None:
            med.expiracion = str(row[2])

        result.append(med)

    cur.close()
    conn.close()
    return result


@app.get("/inventory/medicines/{unidad_salud_id}")
async def get_medicines_by_unidad_salud_id(unidad_salud_id: int) -> dict:
    conn = connect_db()
    cur = conn.cursor()

    query = f"SELECT distinct b.detalle FROM bodega b WHERE b.unidad_salud_id = {unidad_salud_id} and (b.expiracion > current_date or b.expiracion is null)"
    cur.execute(query)
    rows = cur.fetchall()

    if rows is None or len(rows) == 0:
        cur.close()
        conn.close()
        return {"message": "No records found"}

    cur.close()
    conn.close()

    return {
        "found": True,
        "medicines": [row[0] for row in rows]
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

    user_auth = f"set my.app_user = '{account.dpi_auth}'"
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
# ---------------------------------------------- Binnacle.jsx ------------------------------------------------------- #
#######################################################################################################################
@app.get("/binnacle/")
async def get_binnacle() -> list[models.BinnacleResponse] | dict:
    conn = connect_db()
    cur = conn.cursor()
    query = f"SELECT * FROM bitacora order by fecha desc"
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

    # print(patient)

    query_auth = f"set my.app_user = '{patient.dpi_auth}'"
    cur.execute(query_auth)

    query = f"INSERT INTO paciente (dpi, nombre) VALUES ('{patient.dpi}', '{patient.nombre}')"
    try:
        cur.execute(query)
        conn.commit()

        if patient.estatura is not None:
            query = f"UPDATE paciente SET estatura = {patient.estatura} WHERE dpi = '{patient.dpi}'"
            cur.execute(query)
            conn.commit()

        if patient.peso is not None:
            query = f"UPDATE paciente SET peso = {patient.peso} WHERE dpi = '{patient.dpi}'"
            cur.execute(query)
            conn.commit()

        if patient.telefono is not None:
            query = f"UPDATE paciente SET telefono = '{patient.telefono}' WHERE dpi = '{patient.dpi}'"
            cur.execute(query)
            conn.commit()

        if patient.adicciones is not None:
            query = f"UPDATE paciente SET adicciones = '{patient.adicciones}' WHERE dpi = '{patient.dpi}'"
            cur.execute(query)
            conn.commit()

        if patient.direccion is not None:
            query = f"UPDATE paciente SET direccion = '{patient.direccion}' WHERE dpi = '{patient.dpi}'"
            cur.execute(query)
            conn.commit()

        if patient.enfermedades_hereditarias is not None:
            query = f"UPDATE paciente SET enfermedades_hereditarias = '{patient.enfermedades_hereditarias}' WHERE dpi = '{patient.dpi}'"
            cur.execute(query)
            conn.commit()

        cur.close()
        conn.close()

        return {
            "created": True,
        }

    except errors.lookup(UNIQUE_VIOLATION) as e:
        print(e)
        return {
            "created": False,
            "message": "Patient already exists",
            "query": query
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

    query_ver = f"SELECT * FROM paciente WHERE dpi = '{patient.dpi}'"
    cur.execute(query_ver)
    row = cur.fetchone()

    if row is None:
        return {
            "updated": False,
            "message": "Patient does not exist"
        }

    if patient.estatura is not None:
        query = f"UPDATE paciente SET estatura = {patient.estatura} WHERE dpi = '{patient.dpi}'"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            return {
                "updated": False,
                "message": "Error updating patient"
            }

    if patient.peso is not None:
        query = f"UPDATE paciente SET peso = {patient.peso} WHERE dpi = '{patient.dpi}'"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            return {
                "updated": False,
                "message": "Error updating patient"
            }

    if patient.telefono is not None:
        query = f"UPDATE paciente SET telefono = '{patient.telefono}' WHERE dpi = '{patient.dpi}'"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            return {
                "updated": False,
                "message": "Error updating patient"
            }

    if patient.adicciones is not None:
        query = f"UPDATE paciente SET adicciones = '{patient.adicciones}' WHERE dpi = '{patient.dpi}'"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            return {
                "updated": False,
                "message": "Error updating patient"
            }

    if patient.direccion is not None:
        query = f"UPDATE paciente SET direccion = '{patient.direccion}' WHERE dpi = '{patient.dpi}'"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            return {
                "updated": False,
                "message": "Error updating patient"
            }

    if patient.enfermedades_hereditarias is not None:
        query = f"UPDATE paciente SET enfermedades_hereditarias = '{patient.enfermedades_hereditarias}' WHERE dpi = '{patient.dpi}'"
        try:
            cur.execute(query)
            conn.commit()
        except Exception as e:
            print(e)
            return {
                "updated": False,
                "message": "Error updating patient"
            }

    cur.close()
    conn.close()
    return {
        "updated": True
    }


#######################################################################################################################
# ---------------------------------------------- Resultados --------------------------------------------------------- #
#######################################################################################################################
@app.get("/results/deadliest")
async def get_deadliest_diseases() -> list[models.DeadliestDiseases] | dict:
    conn = connect_db()
    cur = conn.cursor()

    query = f"select e.nombre_enfermedad, count(*) as casos from expediente e where e.status = 'Fallecido' group by e.nombre_enfermedad order by casos desc limit 10"

    try:
        cur.execute(query)
        rows = cur.fetchall()

        result = []
        for row in rows:
            result.append(
                models.DeadliestDiseases(
                    nombre_enfermedad=row[0],
                    casos=row[1]
                )
            )

        return {
            "executed": True,
            "result": result
        }
    except Exception as e:
        print(e)
        return {
            "executed": False,
            "message": "Error getting deadliest diseases"
        }


@app.get("/results/most_patients")
async def get_most_patients_by_doctor() -> list[models.MostPatients] | dict:
    conn = connect_db()
    cur = conn.cursor()

    query = f"select m.nombre, count(*) as pacientes_atendidos from medico m inner join expediente e on m.dpi = e.medico_encargado group by m.nombre order by pacientes_atendidos desc limit 10"
    try:
        cur.execute(query)
        rows = cur.fetchall()

        result = []
        for row in rows:
            result.append(
                models.MostPatients(
                    nombre=row[0],
                    cantidad_atendidos=row[1]
                )
            )

        cur.close()
        conn.close()

        return {
            "executed": True,
            "result": result
        }
    except Exception as e:
        print(e)
        cur.close()
        conn.close()
        return {
            "executed": False,
            "message": "Error getting deadliest diseases"
        }


@app.get("/results/most_records/{id_unidad_salud}")
async def get_most_records_by_pacient(id_unidad_salud: int) -> list[models.MostRecords] | dict:
    conn = connect_db()
    cur = conn.cursor()

    query = f"select p.nombre, count(*) as asistencias, p.estatura, p.peso, p.adicciones, p.enfermedades_hereditarias, (p.peso / (p.estatura * p.estatura)) as imc from paciente p inner join expediente e on p.dpi = e.paciente_dpi where e.unidad_salud_id = {id_unidad_salud} group by p.nombre, p.estatura, p.adicciones, p.peso, p.enfermedades_hereditarias order by asistencias desc limit 5"
    try:
        cur.execute(query)
        rows = cur.fetchall()

        result = []
        for row in rows:
            result.append(
                models.MostRecords(
                    nombre=row[0],
                    cantidad_de_expedientes=row[1],
                    estatura=row[2],
                    peso=row[3],
                    adicciones=row[4],
                    enfermedades_hereditarias=row[5],
                    imc=row[6]
                )
            )

        cur.close()
        conn.close()

        return {
            "executed": True,
            "result": result
        }
    except Exception as e:
        print(e)
        cur.close()
        conn.close()
        return {
            "executed": False,
            "message": "Error getting patients with most records"
        }


@app.get("/results/most_patients/healthcenters")
async def get_most_patients_by_unidad_salud() -> list[models.MostPatientsHC] | dict:
    conn = connect_db()
    cur = conn.cursor()

    query = f"select u.nombre, u.tipo, u.direccion, count(*) as pacientes_atendidos from unidad_salud u inner join expediente e on u.id = e.unidad_salud_id group by u.nombre, u.tipo, u.direccion order by pacientes_atendidos desc limit 3"
    try:
        cur.execute(query)
        rows = cur.fetchall()

        result = []
        for row in rows:
            result.append(
                models.MostPatientsHC(
                    nombre_unidad_salud=row[0],
                    tipo=row[1],
                    direccion=row[2],
                    cantidad_atendidos=row[3]
                )
            )

        cur.close()
        conn.close()
        return {
            "executed": True,
            "result": result
        }

    except Exception as e:
        print(e)
        cur.close()
        conn.close()
        return {
            "executed": False,
            "message": "Error getting health centers with most patients"
        }
