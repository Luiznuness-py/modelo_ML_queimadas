# Estratégia de Ingestão e Tratamento de Dados

O projeto vai funcionar da seguinte forma:

Vamos ter os dados que vão se utilizados para criar o modelo de ML.

Esses modelos tem que estar em arquivos .csv.

A partir desses arquivos, vamos abrir um por um aplicar as tratativa nos dados e salvar somente os dados que serão utilizados em um banco de dados.

A trativa vai seguir o seguinte fluxo:

1. Abrir o arquivo

2. Aplicar um filtro onde vamos pegar somente as linhas que atendam aos seguintes requisitos:

   - Valor da coluna 'Pais' seja igual à 'Brasil';
   - Valor da coluna 'Bioma' seja igual à 'Amazônia';
   - Valores das colunas 'FRP', 'DiaSemChuva',  'Precipitacao', 'RiscoFogo', sejam diferente de nulo;
   - Valores das colunas 'FRP', 'DiaSemChuva',  'Precipitacao', 'RiscoFogo', sejam maior ou igual a 0.

A partir disso vamos ter um DataFreme somente com as colunas validas, com isso vamos pegar esse DataFreme e com base nele excluir as linhas validas do DataFreme geral, deixando um DataFreme com as linhas invalidas.

Vamos aplicar uma trativa em cima desse DataFreme com as linhas invalidas onde vamos percorrer sobre as linhas dele verificar se tem alguma linha dentro do DataFreme com linhas validas que corresponde ao mesmo dia e mesmo municipio do que a linha invalida, se tiver ele verifica a distancia entre os locais, se a distancia for menor ou igual a cinto, ele irá trocar os valores que são igual  à -999 pelo valor da linha valida.

Depois que tivermos o DataFreme com todos os dados tratados e pronto iremos  começar fazer a agregação dos dados, criar a classificação dos dados, criar as features e por fim salvar em um banco de dados.
