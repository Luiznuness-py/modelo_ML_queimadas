from datetime import datetime

from sqlalchemy.orm import Mapped

from source.models.base_model import BaseModel


class Dados_CSV(BaseModel):
    __tablename__ = 'data_csv'

    DataHora: Mapped[datetime]
    Satelite: Mapped[str]
    Pais: Mapped[str]
    Estado: Mapped[str]
    Municipio: Mapped[str]
    Bioma: Mapped[str]
    DiaSemChuva: Mapped[str]
    Precipitacao: Mapped[str]
    RiscoFogo: Mapped[str]
    FRP: Mapped[str]
    Latitude: Mapped[str]
    Longitude: Mapped[str]
