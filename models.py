from pydantic import BaseModel


class UserLogin(BaseModel):
    dpi: str
    password: str


class User(BaseModel):
    dpi: str
    nombre: str
    direccion: str
    telefono: str
    num_colegiado: str
    especialidad: str
