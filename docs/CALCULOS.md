# 🌳 Guia de Engenharia de Features para Modelo de Árvores de Decisão

Este documento detalha as etapas de pré-processamento, mesclagem e engenharia de features essenciais para a construção do modelo de classificação de risco de fogo. O objetivo é criar features ricas em padrões temporais e espaciais que otimizem a performance e a velocidade das Árvores de Decisão.

O foco é garantir:
- Consistência temporal e geográfica
- Ausência de *data leakage*
- Features interpretáveis, robustas e eficientes
- Facilidade de manutenção e reprodutibilidade

* **Data leakage:** Data leakage pode ser entendido como vazamento de dados. Ocorre quando o modelo de Machine Learning tem acesso, direta ou indiretamente, a informações que não estariam disponíveis no momento real da predição.

## 1. Pré-Processamento e Mesclagem de Dados

O primeiro passo é consolidar a base de dados.

### 1.1. Mesclagem de Dados
Para garantir que a base de dados esteja completa e alinhada temporalmente e geograficamente, é necessário realizar uma mesclagem de linhas (ou junção/merge) nos datasets de entrada.

* **Chaves de Mesclagem:** As linhas devem ser mescladas usando a combinação das colunas:
    * `Datahora` (coluna temporal)
    * `municipio` (coluna geográfica)
* **Finalidade:** Essa operação é crítica em modelos de ML baseados em séries temporais/geográficas, pois garante que cada observação (`Datahora`/`municipio`) contenha todas as features relevantes para aquele ponto específico, permitindo ao modelo de Árvore de Decisão capturar padrões diários e locais.

* **Exemplo de Implementação:**
    ```python
        df = df.groupby(['Data', 'Municipio']).agg({
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
        df = df_daily.dropna()    
	```

O código a seguir tem como finalidade excluir todas as linhas que contenham o valor -999.0 do calculo que será feito.
	```python
	lambda x: x[x != -999.0]
	```

Quando vamos fazer a agregação dos dados em algumas situações vamos nos deparar com dados -999.0 que são dados com erro. vamos encontrar esses valores nas colunas: FRP, RiscoFogo, DiaSemChuva e Precipitacao.

Primeiro vamos entender como esses dados são gerados:

* **FRP (Fire Radiative Power):**

O FRP é derivado de sensores orbitais (ex.: MODIS, VIIRS) e representa a energia radiativa emitida por focos de fogo, expressa em Megawatts (MW).

O cálculo baseia-se na diferença entre a radiância observada no infravermelho térmico e a radiância de fundo estimada.

* **RiscoFogo (Fire Risk / Fire Danger Index):**

O Risco de Fogo é um índice derivado que representa a probabilidade ou favorabilidade para ocorrência e propagação de incêndios.

Ele é calculado a partir da combinação de variáveis meteorológicas e ambientais, como precipitação acumulada recente, temperatura do ar, umidade relativa, vento e características da vegetação.

* **DiaSemChuva (Dias Sem Precipitação):**

O parâmetro DiaSemChuva representa o número de dias consecutivos desde o último que teve chuva no local.

O cálculo é feito a partir de séries temporais diárias de precipitação, contando-se quantos dias se passaram desde o último registro válido de chuva.

* **Precipitacao (Precipitation):**

A Precipitação corresponde ao volume de água acumulado em um determinado período, geralmente expresso em milímetros.

Os dados são obtidos por radares meteorológico ou sensores orbitais.

* **Possível resolução:**

Como os cáculos pelo pela INPE para chegar no resultado final nós não temos acesso até o momento podemos fazer um def que vai verificar esses valores e ver se outra linha no mesmo local que tenha o valor sem o erro, se tiver ele substitui, se não ele remove a linha por conta do erro.


### 1.2. Criação da Variável Target (Classificação)
A coluna `FRP` (com valores float) deve ser discretizada para criar a variável *target* de classificação (`target_class`). Este é um modelo de **Classificação Multi-Classe** (`Baixo`, `Medio`, `Alto`).

* **Coluna Base:** `FRP` (Float)
* **Exemplo de Implementação:**
    ```python
		def categorizar_frp(self, frp: float) -> str:
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

		if 'FRP' in df.columns:
            df['Categoria_Risco'] = df['FRP'].apply(self.categorizar_frp)
	```

## 2. Engenharia de Features Temporais

A coluna `Datahora` deve ser decomposta em features cíclicas, lineares e não lineares para que o modelo possa interpretar a sazonalidade.

| Feature | Descrição | Propósito |
| :--- | :--- | :--- |
| `dia`, `mes`, `ano`, `diaano` | Extração simples | Componentes lineares de tempo. |
| `Mes_sin`, `Mes_cos` | Sazonalidade (Mensal) | Permite ao modelo capturar o ciclo anual. |
| `DiaAno_sin`, `DiaAno_cos` | Sazonalidade (Anual/Dia do ano) | Permite ao modelo entender a posição do dia no ciclo anual de forma contínua. |

### Fórmulas de Sazonalidade Cíclica (Senoidal e Cossenoidal)
* **Exemplo de Implementação:**
    ```python
		# Lineares
        df['Dia'] = df['Data'].dt.day
        df['Mes'] = df['Data'].dt.month
		df['Ano'] = df['Data'].dt.year
        df['DiaAno'] = df['Data'].dt.dayofyear

		# Não Lineares
		df['Mes_sin'] = np.sin(2 * np.pi * df['Mes'] / 12)
        df['Mes_cos'] = np.cos(2 * np.pi * df['Mes'] / 12)
        df['DiaAno_sin'] = np.sin(2 * np.pi * df['DiaAno'] / 365)
        df['DiaAno_cos'] = np.cos(2 * np.pi * df['DiaAno'] / 365)
	```

## 3. Engenharia de Features de Domínio (Transformações)

As transformações a seguir enriquecem o dataset com informações contextuais e não-lineares.

### 3.1. Features de Interação
As interações ajudam o modelo a capturar relações não-lineares entre indicadores (alto risco de fogo + longo período sem chuva = criticidade).

* **Exemplo de Implementação:**
    ```python
    df['RiscoFogo_x_DiaSemChuva'] = df['RiscoFogo'] * df['DiaSemChuva']
    ```

### 3.2. Expansão Polinomial
Adicionar termos quadráticos permite que o modelo capture curvaturas nas relações entre features e o target.

* **Exemplo de Implementação:**
    ```python
    df['RiscoFogo_squared'] = df['RiscoFogo'] ** 2
    df['DiaSemChuva_squared'] = df['DiaSemChuva'] ** 2
    ```

### 3.3. Features Geográficas Normalizadas
A normalização é crucial para escalas como latitude/longitude, garantindo que elas não dominem as métricas de divisão da árvore por terem valores absolutos muito altos.

* **Exemplo de Implementação:**
    ```python
    lat_min = df['Latitude'].min()
    lat_max = df['Latitude'].max()
    df['Latitude_norm'] = (df['Latitude'] - lat_min) / (lat_max - lat_min)

    lon_min = df['Longitude'].min()
    lon_max = df['Longitude'].max()
    df['Longitude_norm'] = (df['Longitude'] - lon_min) / (lon_max - lon_min)
    ```

### 4. Médias Móveis (Rolling Mean)
Suavizam ruídos e identificam tendências.

* **Implementação:**
    ```python
    # Média Móvel de 7 dias para RiscoFogo
    df['RiscoFogo_media_movel_7'] = df.groupby('Municipio')['RiscoFogo'] \
                                     .transform(lambda x: x.rolling(window=7, min_periods=1).mean().shift(1))
    
    # Média Móvel de 14 dias para DiaSemChuva
    df['DiaSemChuva_media_movel_14'] = df.groupby('Municipio')['DiaSemChuva'] \
                                         .transform(lambda x: x.rolling(window=14, min_periods=1).mean().shift(1))
    ```

### 4.1. Volatilidade (Rolling Std)
Mede a variação local. Alta volatilidade pode ser um indicador de mudança de regime.

* **Implementação:**
    ```python
    df['RiscoFogo_volatilidade_7'] = df.groupby('Municipio')['RiscoFogo'] \
                                       .transform(lambda x: x.rolling(window=7, min_periods=1).std().shift(1).fillna(0))
    ```

### 4.2. Extremos (Rolling Max/Min)
Captura picos ou mínimos severos no histórico recente.

* **Implementação:**
    ```python
    # Máximo risco de fogo nos últimos 14 dias
    df['RiscoFogo_max_14'] = df.groupby('Municipio')['RiscoFogo'] \
                              .transform(lambda x: x.rolling(window=14, min_periods=1).max().shift(1))

    # Mínimo de precipitação nos últimos 7 dias
    df['Precipitacao_min_7'] = df.groupby('Municipio')['Precipitacao'] \
                                .transform(lambda x: x.rolling(window=7, min_periods=1).min().shift(1))
    ```

### 4.3. Acumulação (Rolling Sum)
Útil para métricas como precipitação, onde o total acumulado tem mais significado do que o valor diário.

* **Implementação:**
    ```python
    # Precipitação acumulada nos últimos 7 e 30 dias
    df['Precipitacao_acumulada_7'] = df.groupby('Municipio')['Precipitacao'] \
                                       .transform(lambda x: x.rolling(window=7, min_periods=1).sum().shift(1))
                                       
    df['Precipitacao_acumulada_30'] = df.groupby('Municipio')['Precipitacao'] \
                                        .transform(lambda x: x.rolling(window=30, min_periods=1).sum().shift(1))
    ```


## 5. Features Avançadas Prioritárias

As proxímas features são possíveis testes para deixar o modelo mais completo.

### 5.1. Persistência e Mudança de Padrão (Delta Temporal)

Capturam aceleração ou desaceleração recente das variáveis ambientais, permitindo que a árvore identifique transições de regime.

```python
# Variação diária do risco de fogo
df['RiscoFogo_delta_1'] = df.groupby('Municipio')['RiscoFogo'].diff(1)

# Variação diária da precipitação
df['Precipitacao_delta_1'] = df.groupby('Municipio')['Precipitacao'].diff(1)
```

### 5.2. Indicador Simplificado de Estado de Secura

Traduz o conceito físico de solo seco em uma regra explícita, altamente interpretável e eficiente para árvores.

```python
df['Solo_Seco'] = (
    (df['DiaSemChuva'] > 7) &
    (df['Precipitacao_acumulada_7'] < 5)
).astype(int)
```

### 5.3. Frequência Recente de Eventos de Fogo

Captura reincidência de fogo no curto prazo, um dos sinais mais fortes para previsão de risco.

```python
# Número de dias com ocorrência de fogo nos últimos 7 dias
df['Dias_com_Fogo_7'] = (
    df.groupby('Municipio')['FRP']
      .transform(lambda x: (x > 0).rolling(7).sum().shift(1))
)
```