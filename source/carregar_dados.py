from pathlib import Path

import pandas as pd

from source.core.settings import Settings
from source.resources.logging import get_logger
from source.resources.tools import _time_run


logger = get_logger()

from math import radians, cos, sin, asin, sqrt

def distancia_haversine(lat1, lon1, lat2, lon2):
    # Raio da Terra em km
    # A Terra é como se fosse uma bola, então ela tem um raio, 
    # que é a distancia do centro até a superficie.
    # O valor 6471 é um valor padrão usado em cálculos de distância geográfica.
    R = 6371
    
    # Latitude e longitude são dados em graus (0-360°), mas a trigonometria (sin, cos) trabalha com radianos (0-2π). Por isso convertemos.
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Tiramos a diferença para consegue calcular em KM
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Essa fórmula calcula a diferença angular entre os dois pontos na esfera terrestre:
    # sin(dlat/2)**2 → quanto você subiu/desceu (latitude)
    # cos(lat1) * cos(lat2) * sin(dlon/2)**2 → quanto você se moveu lateralmente (longitude)
    # O cos(lat1) e cos(lat2) aparecem porque as linhas de longitude ficam mais próximas perto dos polos
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2

    # Se você sabe o ângulo entre dois pontos na esfera (em radianos), multiplica pelo raio da Terra para ter a distância em km.
    c = 2 * asin(sqrt(a)) # 'c' é o ângulo em radianos
    
    return R * c  # Transforma ângulo em quilômetros

def verificar_menor_distancia(df_dados_localizados: pd.DataFrame, row:pd.Series):
    
    distancia = {}
    
    for _, rows in df_dados_localizados.iterrows():

        distancia[_] = distancia_haversine(
            lat1=float(row['Latitude']),
            lon1=float(rows['Longitude']),
            lat2=float(rows['Latitude']),
            lon2=float(row['Longitude']),
        )

    distancia = dict(sorted(distancia.items(), key=lambda x: x[1]))

    return next(iter(distancia.items()))

def inserir_dados(row: pd.Series, df_dados_localizados: pd.Series, campos_com_erros: list[str]):
    
    for campo in campos_com_erros:

        if row[campo] == -999:

            row[campo] = df_dados_localizados[campo]
    
    return row

def buscar_por_valor(row, df: pd.DataFrame, campos_com_erros: list[str]) -> bool | list:
    
    df_dados_localizados = df.loc[
        (df['Data'] == row['Data']) &
        (df['Municipio'] == row['Municipio'])
    ].reset_index(drop=True)

    if df_dados_localizados.empty:
        return None
    
    distancia = None
    
    if len(df_dados_localizados) == 1:

        if (row['Latitude'] == df_dados_localizados['Latitude'].iloc[0]) and \
            (row['Longitude'] == df_dados_localizados['Longitude'].iloc[0]):

            row = inserir_dados(
                row=row,
                df_dados_localizados=df_dados_localizados.loc[0],
                campos_com_erros=campos_com_erros,
            )

            return row
            
        distancia = distancia_haversine(
                lat1=float(row['Latitude']),
                lon1=float(df_dados_localizados['Longitude'].iloc[0]),
                lat2=float(df_dados_localizados['Latitude'].iloc[0]),
                lon2=float(row['Longitude']),
        )

        if distancia <= 5:

            row = inserir_dados(
                row=row,
                df_dados_localizados=df_dados_localizados.loc[0],
                campos_com_erros=campos_com_erros,
            )

            return row

        return None

    distancia = verificar_menor_distancia(
                        df_dados_localizados=df_dados_localizados,
                        row=row,
                    )

    if distancia[1] <= 5:

        row = inserir_dados(
                row=row,
                df_dados_localizados=df_dados_localizados.loc[distancia[0]],
                campos_com_erros=campos_com_erros,
        )

        return row

    return None


def carregar_dados(settings: Settings):
    logger.info(f"{settings.APP_NAME} - v{settings.APP_VERSION}")

    path_resources = Path(settings.PATH_ARQUIVOS_CSV)
    files = list(path_resources.glob("*.csv"))

    df_completo = None

    for csv_path in files:

        df = pd.read_csv(csv_path, sep=",")

        df['Latitude'] = df['Latitude'].str.replace(',', '.').astype(float)
        df['Longitude'] = df['Longitude'].str.replace(',', '.').astype(float)

        df['Data'] = pd.to_datetime(df['DataHora']).dt.date

        logger.info(f"Arquivo encontrado: {csv_path.name} - {len(df)}")

        campos_com_erros = [
            'FRP', 
            'DiaSemChuva', 
            'Precipitacao', 
            'RiscoFogo',
        ]

        campos_obrigatorios = campos_com_erros + [ 
            'Latitude', 
            'Longitude', 
            'DataHora', 
            'Satelite'
        ]

        df_dados_utilizados = df.loc[
            (df['Pais'] == 'Brasil') &
            (df['Bioma'] == 'Amazônia') &
            (df[campos_obrigatorios].notnull().all(axis=1)) &
            (df[campos_com_erros] >= 0).all(axis=1)
        ]

        df = df.drop(
            df_dados_utilizados.index\
        ).reset_index(drop=True)

        print(len(df))

        df = df.apply(
            buscar_por_valor, 
            axis=1, 
            args=(df_dados_utilizados, campos_com_erros)
        ).dropna(inplace=True)
        
        try:
            if not df_completo:
                df_completo = df
                continue
        except ValueError:
            pass
        
        pd.concat(
            [df_completo, df], 
            join='outer', 
            ignore_index=True,
            sort=False
        )

    print()