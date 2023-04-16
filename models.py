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


class RecordSearch(BaseModel):
    dpi: str


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


class BodegaSearch(BaseModel):
    id: int


class Bodega(BaseModel):
    id: int
    detalle: str
    cantidad: int
    expiracion: str
    unidad_salud_id: int


class InventoryUpdate(BaseModel):
    id: int
    existencia: int


class ProductAdd(BaseModel):
    id_user_auth: str
    detalle: str
    cantidad: int
    expiracion: str
    unidad_salud_id: int


class AccountRequest(BaseModel):
    dpi: str


class AccountDetails(BaseModel):
    dpi: str
    nombre: str
    direccion: str
    telefono: str
    num_colegiado: str
    especialidad: str
    unidad_salud_id: int


class WorkHistory(BaseModel):
    fecha_entrada: str
    fecha_salida: str | None
    medico_dpi: str
    unidad_salud_id: int


class WorkHistoryUpdate(BaseModel):
    medico_dpi: str
    unidad_salud_id: int


class AccountUpdate(BaseModel):
    dpi: str
    direccion: str
    telefono: str
    especialidad: str


class MedicineSearch(BaseModel):
    unidad_salud: str


class MedicineResponse(BaseModel):
    id: int
    detalle: str


