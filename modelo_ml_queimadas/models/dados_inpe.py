from datetime import datetime

from sqlalchemy.orm import Mapped

from modelo_ml_queimadas.models.base_model import BaseModel


class Dados_Inpe(BaseModel):
    __tablename__ = 'dados_inpe'

    data: Mapped[datetime]
    setelite: Mapped[str]
    pais: Mapped[str]
    estado: Mapped[str]
    municipio: Mapped[str]
    bioma: Mapped[str]
    diasemchuva: Mapped[int]
    precipitacao: Mapped[float]
    riscofogo: Mapped[float]
    frp: Mapped[float]
    latitude: Mapped[float]
    longitude: Mapped[float]
