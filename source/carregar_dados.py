import numpy as np
from pathlib import Path
from math import radians, cos, sin, asin, sqrt

import pandas as pd
from sqlalchemy import text

from source.core.settings import Settings
from source.resources.tools import _time_run
from source.resources.logging import get_logger
from source.core.database import get_sync_engine


logger = get_logger()


@_time_run
def create_table(engine):
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS dados_csv (
            Ano INTEGER,
            Mes INTEGER,
            Dia INTEGER,
            DiaAno INTEGER,
            Mes_cos FLOAT,
            Mes_sin FLOAT,
            Municipio TEXT,
            RiscoFogo FLOAT,
            DiaAno_sin FLOAT,
            DiaAno_cos FLOAT,
            DiaSemChuva INTEGER,
            Precipitacao FLOAT,
            Latitude_norm FLOAT,
            Longitude_norm FLOAT,
            RiscoFogo_max_14 FLOAT,
            RiscoFogo_squared FLOAT,
            Precipitacao_min_7 FLOAT,
            DiaSemChuva_squared FLOAT,
            RiscoFogo_x_DiaSemChuva FLOAT,
            RiscoFogo_media_movel_7 FLOAT,
            Precipitacao_acumulada_7 FLOAT,
            Precipitacao_acumulada_30 FLOAT,
            DiaSemChuva_media_movel_14 FLOAT,
            Precipitacao_media_movel_7 FLOAT
        )
    """)) 


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

@_time_run
def carregar_dados(settings: Settings):
    logger.info(f"{settings.APP_NAME} - v{settings.APP_VERSION}")

    engine = get_sync_engine()
    create_table(engine)

    path_resources = Path(settings.PATH_ARQUIVOS_CSV)
    files = list(path_resources.glob("*.csv"))

    for csv_path in files:

        df = pd.read_csv(csv_path, sep=",")

        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

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
        
        df = pd.concat(
            [df_dados_utilizados, df], 
            join='outer', 
            ignore_index=True,
            sort=False
        )

        # Função que faz a agregação dos dados por dia e municipio.
        df = agregar_por_dia_municipio(df=df)

        # Função que cria uma coluna no DataFreme com base no valor de FRP.
        df = criar_categorias_risco(df=df)

        # Função que faz a criação das features.
        df = engenharia_features(df=df)

        insert_fast(engine, df)
        logger.info(f"{csv_path.name} finalizado.")

        print()

    print()

@_time_run
def insert_fast(engine, df: pd.DataFrame):
    conn = engine.raw_connection()
    cur = conn.cursor()

    for i in range(0, len(df), 5000):
        chunk = df.iloc[i:i+5000]
        values = chunk.values.tolist()
        cur.executemany(
            "INSERT INTO dados_csv VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            values
        )
    conn.commit()

@_time_run
def agregar_por_dia_municipio(df: pd.DataFrame) -> pd.DataFrame:
    """
        Nesta função será feito a agregação dos dados apartir de dia por data e municipio, ou seja, 
        para cada dia que o datafreme tem ele vai separar as linhas de um unico dia e municipio e efetuar
        alguns calculos que são passados na função: agg.

    Args:
        df (pd.DataFrame): DataFreme onde será feito a agregação dos dados.

    Returns:
        pd.DataFrame: DataFreme com os dados agregados.
    """
    logger.info("Agregando dados por dia e município...")

    df = df.copy()
    
    # Transforma a coluna ´DataHora´ em datetime.
    df['DataHora'] = pd.to_datetime(df['DataHora'])
    # A coluna ´DataHora´ tem data e hora, então a linha de código abaixo cria uma coluna chamada ´Data´ que pega somente a data da coluna ´DataHora´.
    df['Data'] = df['DataHora'].dt.date

    # Essas linhas de código iram fazer a agregação dos dados por dia e muncipio além de fazer alguns calculos que são definidos no metodo agg().
    df_daily = df.groupby(['Data', 'Municipio']).agg({
        'FRP': 'sum',
        
        # Para RiscoFogo: média apenas dos valores válidos
        'RiscoFogo': lambda x: x[x != -999.0].mean(),
        
        # Para DiaSemChuva: máximo apenas dos valores válidos
        'DiaSemChuva': lambda x: x[x != -999.0].max(),
        
        # Para Precipitacao: média apenas dos valores válidos
        'Precipitacao': lambda x: x[x != -999.0].mean(),
        
        'Latitude': 'mean',
        'Longitude': 'mean'
    }).reset_index()

    # Exclui as linhas que tem algum valor como NaN.
    df_daily = df_daily.dropna()

    # Transforma a coluna ´Data´ em datetime.
    df['Data'] = pd.to_datetime(df['Data'])

    logger.info("✓ Dados agregados por dia e município com sucesso!")

    return df_daily


@_time_run
def criar_categorias_risco(df: pd.DataFrame) -> pd.DataFrame:
    """
        Cria categorias de risco baseado em FRP.
        Baixo: FRP < 100
        Médio: 100 <= FRP < 500
        Alto: FRP >= 500

    Args:
        df (pd.DataFrame): DataFreme que tem que ser aplicado a cateforia dos dados.

    Returns:
        pd.DataFrame: Retorna o DataFreme recebido com a coluna ´Categoria_Risco´ com a categoria criada.
    """
    logger.info("Criando categorias de risco baseadas em FRP...")

    df = df.copy()

    if 'FRP' in df.columns:
        df['Categoria_Risco'] = df['FRP'].apply(categorizar_frp)
    
    logger.info("✓ Categorias de risco criadas com sucesso!")

    return df


@_time_run
def categorizar_frp(frp: float) -> str:
    """
        Categoriza o FRP em Baixo, Médio e Alto.
        
    Args:
        frp (float): Valor do FRP

    Returns:
        str: Cateoria do FRP
    """
    if frp < 100:
        return 'Baixo'
    elif frp < 500:
        return 'Médio'
    else:
        return 'Alto'


@_time_run
def engenharia_features(df: pd.DataFrame) -> pd.DataFrame:
    """
        Está função é utilizada para criar as features com base nas colunas do DataFreme original,
        essas features são criadas para que o modelo tenha mais conhecimento sobre os dados e ele
        consiga predizer o dado determiando como target de uma forma mais eficiente.

    Args:
        df (pd.DataFrame): DataFreme que será utilizado para criar as features.

    Returns:
        pd.DataFrame: DataFreme com as features criadas.
    """

    logger.info("Aplicando engenharia de features...")
    df = df.copy()

    df['Data'] = pd.to_datetime(df['Data'])

    # ===== FEATURES TEMPORAIS =====
    df['Ano'] = df['Data'].dt.year
    df['Mes'] = df['Data'].dt.month
    df['Dia'] = df['Data'].dt.day
    df['DiaAno'] = df['Data'].dt.dayofyear

    # ===== FEATURES LÓGICAS =====
    # Nós criamos essas features para que o modelo entenda que os valores 'Dia' e 'Mes'
    # não são valores continuos, eles tem uma lógica por trás. 
    # A forma com que implementamos isso é como se criassemos um relógio onde cada valor 
    # tem sua posição dentro dele e toda vez que o ultimo valor do relógio é atingido
    # o ciclo se reinicia e volta para o valor inicial.
    # Criamos essa features por que se mantivessemos as features somente como 'Dia' e 'Mes'
    # o modelo iria entender esses valores como valores continuos, mas na verdade não são.
    df['Mes_sin'] = np.sin(2 * np.pi * df['Mes'] / 12)
    df['Mes_cos'] = np.cos(2 * np.pi * df['Mes'] / 12)
    df['DiaAno_sin'] = np.sin(2 * np.pi * df['DiaAno'] / 365)
    df['DiaAno_cos'] = np.cos(2 * np.pi * df['DiaAno'] / 365)

    # ===== FEATURES DE INTERAÇÃO =====
    # Essa feature é importante para determinar o Risco das queimadas, ou seja, se estiver tendo fogo e chuva 
    # o perigo não é tão alto, agora se estiver com Risco de Fogo e não estiver chovendo o perigo é grande.
    # Então seria uma forma de entender qual o Risco da queimada que está ou irá acontecer.
    df['RiscoFogo_x_DiaSemChuva'] = df['RiscoFogo'] * df['DiaSemChuva']

    # ===== FEATURES EXPANÇÃO POLINOMIAL =====
    # Utilizamos o conceito de expansão polinomial para entendermos a não linearidade dos dados e o modelo 
    # conseguir predizer de uma forma mais acertiva.
    df['RiscoFogo_squared'] = df['RiscoFogo'] ** 2
    df['DiaSemChuva_squared'] = df['DiaSemChuva'] ** 2

    # ===== FEATURES GEOGRÁFICAS NORMALIZADAS =====
    # Aqui normalizamos a Latitude e Longitude para igualar a importância numérica, assim o modelo não entende que 
    # a Latitude e Longitude tem mais importância do que os demais parametros.
    df['Latitude_norm'] = (df['Latitude'] - df['Latitude'].min()) / (df['Latitude'].max() - df['Latitude'].min())
    df['Longitude_norm'] = (df['Longitude'] - df['Longitude'].min()) / (df['Longitude'].max() - df['Longitude'].min())
    
    # ===== FEATURES DE MÉDIA MÓVEL =====
    # A média móvel nos permite suavizar as flutuações dos dados e capturar tendências locais.
    # Ao agruparmos por Município, conseguimos entender o comportamento histórico de cada região.
    # Utilizamos janelas diferentes (7 e 14 dias) para capturar padrões em diferentes escalas de tempo.
    # Isso ajuda o modelo a identificar se o Risco de Fogo está aumentando ou diminuindo em uma tendência.
    df['RiscoFogo_media_movel_7'] = df.groupby('Municipio')['RiscoFogo'].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )
    df['Precipitacao_media_movel_7'] = df.groupby('Municipio')['Precipitacao'].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )
    df['DiaSemChuva_media_movel_14'] = df.groupby('Municipio')['DiaSemChuva'].transform(
        lambda x: x.rolling(window=14, min_periods=1).mean()
    )

    # ===== FEATURES DE VOLATILIDADE =====
    # A volatilidade mede a variação dos dados em um período de tempo.
    # Se a volatilidade do Risco de Fogo é alta, significa que os valores estão mudando drasticamente,
    # o que pode indicar condições instáveis ou críticas para queimadas em um Município.
    # Da mesma forma, a volatilidade da Precipitação nos ajuda a entender se a chuva está ocorrendo
    # de forma consistente ou irregular, impactando na prevenção de incêndios.
    df['RiscoFogo_volatilidade_7'] = df.groupby('Municipio')['RiscoFogo'].transform(
        lambda x: x.rolling(window=7, min_periods=1).std().fillna(0)
    )
    df['Precipitacao_volatilidade_7'] = df.groupby('Municipio')['Precipitacao'].transform(
        lambda x: x.rolling(window=7, min_periods=1).std().fillna(0)
    )

    # ===== FEATURES DE EXTREMOS =====
    # Essas features capturam os valores extremos (máximos e mínimos) em janelas de tempo específicas.
    # O valor máximo do Risco de Fogo em 14 dias nos mostra o pior cenário possível em um Município,
    # ajudando o modelo a identificar períodos críticos de risco elevado.
    # O valor mínimo de Precipitação em 7 dias indica períodos de seca, que são condições favoráveis
    # para o surgimento e propagação de queimadas.
    df['RiscoFogo_max_14'] = df.groupby('Municipio')['RiscoFogo'].transform(
        lambda x: x.rolling(window=14, min_periods=1).max()
    )
    df['Precipitacao_min_7'] = df.groupby('Municipio')['Precipitacao'].transform(
        lambda x: x.rolling(window=7, min_periods=1).min()
    )

    # ===== FEATURES DE ACUMULAÇÃO =====
    # A acumulação de Precipitação em períodos específicos nos permite entender quanto total de chuva
    # caiu em um Município ao longo de dias ou meses.
    # Com uma janela de 7 dias, capturamos o impacto das chuvas recentes na umidade do solo e vegetação.
    # Com uma janela de 30 dias, capturamos a tendência de precipitação em um período mais longo,
    # que afeta a disponibilidade de água e a ressecação da vegetação, influenciando o risco de queimadas.
    df['Precipitacao_acumulada_7'] = df.groupby('Municipio')['Precipitacao'].transform(
        lambda x: x.rolling(window=7, min_periods=1).sum()
    )
    df['Precipitacao_acumulada_30'] = df.groupby('Municipio')['Precipitacao'].transform(
        lambda x: x.rolling(window=30, min_periods=1).sum()
    )
    
    logger.info(f"✓ Features avançadas criadas com sucesso! Total: {df.shape[1]}")
    
    return df