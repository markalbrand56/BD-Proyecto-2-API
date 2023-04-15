from pydantic import BaseModel


class User(BaseModel):
    dpi: str
    rol: str
    password: str


class UserLogin(BaseModel):
    dpi: str
    password: str


class UserSignIn(BaseModel):
    dpi: str
    nombre: str
    direccion: str
    telefono: str
    num_colegiado: str
    especialidad: str
    unidad_de_salud: int
    rol: str
    password: str


class UserDetails(BaseModel):
    dpi: str
    nombre: str
    direccion: str
    telefono: str
    num_colegiado: str
    especialidad: str
    unidad_de_salud: int


class RecordSearch(BaseModel):
    dpi: str


'''
no_expediente serial primary key,
    paciente_dpi varchar(30),
    medico_encargado varchar(30),
    enfermedad_id int,
    examenes text,
    diagnosticos text,
    fecha_atencion date,
    cirugias text,
    status text,
    unidad_salud_id int,
'''


class Record(BaseModel):
    no_expediente: int
    paciente_dpi: str
    medico_encargado: str
    enfermedad_id: int
    examenes: str
    diagnosticos: str
    fecha_atencion: str
    cirugias: str
    status: str
    unidad_salud_id: int
