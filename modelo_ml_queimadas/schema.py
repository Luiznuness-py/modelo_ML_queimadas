from datetime import datetime

from pydantic import BaseModel


class Dados(BaseModel):
    data: datetime
    setelite: str
    pais: str
    estado: str
    municipio: str
    bioma: str
    diasemchuva: int
    precipitacao: float
    riscofogo: float
    frp: float
    latitude: float
    longitude: float