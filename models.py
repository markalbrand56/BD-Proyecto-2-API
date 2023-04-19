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
    unidad_de_salud_nombre: str
    rol: str
    password: str


class UserDetails(BaseModel):
    dpi: str
    nombre: str
    direccion: str
    telefono: str
    num_colegiado: str
    especialidad: str


class UserDetailsUpdate(BaseModel):
    dpi: str
    nombre: str
    direccion: str
    telefono: str
    num_colegiado: str
    especialidad: str
    unidad_salud_id: int


class UserSuccessLogin(BaseModel):
    dpi: str
    rol: str


class Record(BaseModel):
    no_expediente: int
    paciente_dpi: str
    medico_encargado: str
    enfermedad_id: int | None
    examenes: str | None
    diagnosticos: str | None
    fecha_atencion: str
    cirugias: str | None
    status: str
    unidad_salud_id: int


class NewRecord(BaseModel):
    paciente_dpi: str
    medico_encargado: str
    enfermedad_id: int | None
    examenes: str | None
    diagnosticos: str | None
    fecha_atencion: str
    fecha_salida: str | None  # Cierre de expediente
    cirugias: str | None
    status: str | None
    unidad_salud_id: int
    dpi_auth: str
    medicamentos: list[int] | None


class BodegaSearch(BaseModel):
    nombre_unidad_salud: str


class Bodega(BaseModel):
    id: int
    detalle: str
    cantidad: int
    expiracion: str | None
    unidad_salud_id: int


class InventoryUpdate(BaseModel):
    id: int
    existencia: int
    dpi_auth: str


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
    dpi_auth: str


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


class BinnacleResponse(BaseModel):
    accion: str
    tabla: str
    fecha: str
    usuario_dpi: str
    usuario: str | None


class HealthCenter(BaseModel):
    id: int
    tipo: str
    nombre: str
    direccion: str
