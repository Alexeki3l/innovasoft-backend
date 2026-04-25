from pydantic import BaseModel
from datetime import datetime

class ListRequest(BaseModel):
    identificacion: str | None = None
    nombre: str | None = None
    usuarioId: str

class CreateRequest(BaseModel):
    nombre: str
    apellidos:str
    identificacion:str
    celular: str
    otroTelefono: str
    direccion: str
    fNacimiento: datetime
    fAfiliacion: datetime
    sexo: str
    resennaPersonal: str
    imagen:str
    interesFK: str
    usuarioId: str