# Estratégia de Ingestão e Tratamento de Dados

Assim como foi entendi anteriormente ter uma base de dados e passar os dados para outra base de dados não é muito viável, então podemos fazer isso de uma forma um pouco diferente. Em vez de pegar os dados e só incluirmos no DB vamos ler os arquivos CSV aplicar as tratativas dos dados que são: mesclagem, classificação e criação de features (podendo ter tratamento dos valores com erro como -999.0), depois de fazer essas tratativas incluir os valores no banco de dados (acredito que essa já seja a ideia inicial mas só pra deixar explicito que vamos seguir dessa forma). Para fazer isso temos que estabelecer quais vão ter as features e target utilizado na criação do modelo para que consigamos criar o DB com a tabela de colunas corretas para armazenar os dados tratados.

1. A primeira forma e mais simples é criar um DataFreme geral com pandas, que irá armazenar todos os valores dos arquivos CSV. Abrir cada arquivo CSV e aplicar um .concat no DataFreme geral para no final fazer a tratativa dos dados e incluir os valores no DB.

2. Podemos fazer a mesmo coisa que a anterior só que em vez de abrir um arquivo CSV completo em memoria abrir ele com chuncks e incluir as chunks no arquivo CSV geral com o .concat.

3. A forma mais eficiente acredito que seja abrir os arquivos CSV através de chunks, fazer a tratativa dos dados em cima das chunks e por final adiciona-las no DB. Dessa forma não teremos grandes volumes de dados em memoria e temos uma logica bem definida.

