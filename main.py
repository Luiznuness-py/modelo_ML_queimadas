import pandas as pd
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from source.core.settings import settings
from source.core.database import Base, get_sync_engine, get_db

print(f"{settings.APP_NAME} - v{settings.APP_VERSION}")

data = str(settings.PATH_ARQUIVOS_CSV + "\\dbqueimadas_CSV\\dados_2014.csv")

engine = get_sync_engine()

df = pd.read_csv(data, sep=",", nrows=10)
df.to_sql('dados_csv', con=engine, if_exists='append', index=False)

df_banco = pd.read_sql("SELECT * FROM dados_csv", engine)
    
print(df.head())