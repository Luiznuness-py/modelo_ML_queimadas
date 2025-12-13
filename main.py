import pandas as pd
from pathlib import Path
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from source.core.settings import settings
from source.core.database import Base, get_sync_engine, get_db
from source.resources.logging import get_logger
from source.resources.tools import _time_run
import sqlite3

logging = get_logger()

@_time_run
def insert_fast(engine, csv_path: Path):
    conn = engine.raw_connection()
    cur = conn.cursor()

    for chunk in pd.read_csv(csv_path, chunksize=5000):
        values = chunk.values.tolist()
        cur.executemany(
            "INSERT INTO dados_csv VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            values
        )
    conn.commit()

@_time_run
def create_table(engine):
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS dados_csv (
            DataHora TEXT,
            Satelite TEXT,
            Pais TEXT,
            Estado TEXT,
            Municipio TEXT,
            Bioma TEXT,
            DiaSemChuva INTEGER,
            Precipitacao FLOAT,
            RiscoFogo FLOAT,
            FRP FLOAT,
            Latitude FLOAT,
            Longitude FLOAT
        )
    """))
    

logging.info(f"{settings.APP_NAME} - v{settings.APP_VERSION}")

path_resources = Path(settings.PATH_ARQUIVOS_CSV)
files = list(path_resources.glob("*.csv"))

engine = get_sync_engine()
create_table(engine)

for csv_path in files:
    # df = pd.read_csv(csv_path, sep=",", nrows=10)
    logging.info(f"Inserindo arquivo: {csv_path.name}")
    insert_fast(engine, csv_path)
    logging.info(f"{csv_path.name} finalizado.")


df_banco = pd.read_sql("SELECT * FROM dados_csv", engine)
    
print(df_banco.head())
print(df_banco.shape)