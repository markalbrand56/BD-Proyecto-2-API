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
    examenes: str | None
    diagnosticos: str | None
    fecha_atencion: str
    fecha_salida: str | None  # Cierre de expediente
    cirugias: str | None
    status: str
    unidad_salud_id: int
    enfermedad: int | None
    evolucion: str | None


class NewRecord(BaseModel):
    paciente_dpi: str
    medico_encargado: str
    enfermedad: str | None
    evolucion: str | None
    examenes: str | None
    diagnosticos: str | None
    fecha_atencion: str
    fecha_salida: str | None  # Cierre de expediente
    cirugias: str | None
    status: str | None
    unidad_salud_id: int
    dpi_auth: str
    medicamentos: list[int] | None


class UpdateRecord(BaseModel):
    no_expediente: int
    paciente_dpi: str
    medico_encargado: str | None
    examenes: str | None
    diagnosticos: str | None
    fecha_atencion: str | None
    fecha_salida: str | None  # Cierre de expediente
    cirugias: str | None
    status: str | None
    unidad_salud_id: int | None
    enfermedad: str | None
    evolucion: str | None
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


class BodegaMedicinasVencidas(BaseModel):
    id_en_bodega: int
    unidad_salud_id: int
    detalle: str
    cantidad: int


class BodegaMedicinasPorVencer(BaseModel):
    id_en_bodega: int
    unidad_salud_id: int
    detalle: str
    fecha_expiracion: str
    cantidad_en_bodega: int


class MedicinasBajoStock(BaseModel):
    unidad_salud_id: int
    detalle: str
    cantidad_minima: int
    cantidad_en_bodega: int


class InventoryUpdate(BaseModel):
    id: int
    existencia: int
    dpi_auth: str


class ProductAdd(BaseModel):
    id_user_auth: str
    detalle: str
    cantidad: int
    cantidad_minima: int | None
    expiracion: str | None
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
    dpi_auth: str


class MedicineSearch(BaseModel):
    unidad_salud: str


class MedicineResponse(BaseModel):
    id: int
    detalle: str
    expiracion: str | None


class MedicinaExpediente(BaseModel):
    medicamento: str
    cantidad: int


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


class HealthCenterName(BaseModel):
    nombre: str


class PatientDetails(BaseModel):
    dpi: str
    nombre: str
    estatura: float | None
    peso: float | None
    telefono: str | None
    adicciones: str | None
    direccion: str | None
    enfermedades_hereditarias: str | None


class PatientCreate(BaseModel):
    dpi: str
    nombre: str
    estatura: float | None
    peso: float | None
    telefono: str | None
    adicciones: str | None
    direccion: str | None
    enfermedades_hereditarias: str | None
    dpi_auth: str


class PatientUpdate(BaseModel):
    dpi: str
    nombre: str | None
    estatura: float | None
    peso: float | None
    telefono: str | None
    adicciones: str | None
    direccion: str | None
    enfermedades_hereditarias: str | None
    dpi_auth: str


class DeadliestDiseases(BaseModel):
    nombre_enfermedad: str
    casos: int


class MostPatients(BaseModel):
    nombre: str
    cantidad_atendidos: int


class MostRecords(BaseModel):
    nombre: str
    cantidad_de_expedientes: int
    estatura: float | None
    peso: float | None
    addicciones: str | None
    enfermedades_hereditarias: str | None
    imc: float | None


class MostPatientsHC(BaseModel):
    nombre_unidad_salud: str
    tipo: str
    direccion: str
    cantidad_atendidos: int
