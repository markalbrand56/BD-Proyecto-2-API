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


class RecordSearch(BaseModel):
    dpi: str
