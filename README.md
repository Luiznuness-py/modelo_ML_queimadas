# Projeto de ML: Previsão de Queimadas no Bioma da Amazônia

Este projeto visa desenvolver e implementar um Sistema Preditivo de Queimadas através de Machine Learning, focado em alta precisão e automação. O objetivo é construir um modelo de classificação supervisionada capaz de prever a probabilidade de ocorrência de novos focos de calor em áreas geográficas específicas do Bioma Amazônico.

**Visão Geral**: modelo de classificação (ocorrência / não-ocorrência de queimadas) com baseline em Random Forest e otimização com XGBoost.

**Conteúdo deste README**
- **Objetivo e Metodologia:** descrição do problema e abordagem.
- **Estrutura e Ferramentas:** componentes escolhidos e finalidades.
- **Ingestão de Dados:** fontes e features principais.
- **Modelos:** Random Forest e XGBoost — motivações e uso.
- **Setup Local:** instruções com `docker-compose` e `poetry`.

**Objetivo e Metodologia**

- **Objetivo:** Construir um modelo de classificação que faz previsões de queimadas no Bioma da Amazônia.
- **Metodologia:** seguir um ciclo padrão de projeto de ML: ingestão e validação dos dados, engenharia de features, treino e validação, baseline com Random Forest, tentativa de ganho com XGBoost, análise de interpretabilidade.

**Estrutura e Ferramentas**

- **Ambiente/Dependências:** `poetry` — gerenciador de dependências e ambiente virtual.
- **Containerização / Orquestração:** `docker` + `docker-compose` — executar serviços isolados (app e PostgreSQL).
- **Banco de Dados:** `PostgreSQL` — armazenar séries históricas de focos e features processadas.
- **ORM/Persistência:** `sqlalchemy[asyncio]` + `psycopg[binary]` — mapeamento objeto-relacional e acesso ao DB.
- **Validação de Dados:** `pydantic` — schemas para validar payloads antes da persistência.
- **Tramento de Dados:** `pandas` + `numpy` — fazer o tratamento dos dados em formato tabular, facilitando na hora de treinar o modelo.
- **Criação do Modelo:** `scikit-learn` — criação e validação de algoritmos de ML.

**Fontes de Dados**

Uma previsão confiável depende da qualidade e diversidade das features.

- **Fonte de dados utilizada:** Para extrair os dados será utilizado DBQueimadas, base oficial da INPE que é muito utiliza para acessar dados de queimadas. Os dados seram extraidos em arquivos CSV.  

**Seleção e Funcionamento dos Algoritmos**

O problema é de classificação em dados tabulares com relações não-lineares; priorizamos modelos baseados em árvores.

**Machine Learning**

Quando falamos de Machine Learning temos que pensar nos diversos algoritmos que podemos utilizar para criar um modelo. Isso pode ocasionar
em algumas duvinas na hora de escolher um algoritmo para criar seu modelo. Então segue alguns entendimentos que são cruciais de serem entendidas para escolher um bom algoritmo para criar seu modelo.

# Como Escolher o Melhor Algoritmo de Machine Learning

A escolha do algoritmo de Machine Learning não é baseada em intuição, mas em uma análise estruturada. Para selecionar o modelo adequado, é necessário compreender quatro fundamentos: o tipo de problema, as características dos dados, a necessidade de interpretabilidade e a complexidade do cenário.

## Entender o Tipo de Problema

A definição do problema elimina a maior parte dos algoritmos. É necessário identificar qual tarefa está sendo realizada:

- **Classificação:** previsão de categorias (ex.: Queimada = 1, Não Queimada = 0).  
  *Exemplos:* Random Forest, XGBoost, Regressão Logística, SVM, KNN.

- **Regressão:** previsão de valores contínuos.  
  *Exemplos:* Regressão Linear, Random Forest Regressor, Redes Neurais.

- **Clusterização:** agrupamento de dados não rotulados.  
  *Exemplos:* K-Means, DBSCAN.

- **Séries Temporais:** previsão sequencial dependente do tempo.  
  *Exemplos:* LSTM, ARIMA.

Identificar corretamente a tarefa direciona automaticamente a lista de modelos adequados.

## Analisar as Características dos Dados

Os dados definem quais algoritmos funcionam melhor. Os pontos mais importantes são:

- **Formato Tabular:** Random Forest, XGBoost e LightGBM são superiores em dados estruturados.
- **Relações Não Lineares:** RF, XGBoost, SVM e Redes Neurais lidam melhor com complexidade.
- **Tamanho do Dataset:**  
  - Pequeno: RF e SVM têm melhor performance.  
  - Grande: LightGBM e Redes Neurais escalam melhor.
- **Tipos de Features:**  
  - Árvores -> não exigem escalonamento (evita que uma feature/parametro com números grandes domine outra com números pequenos).
  - SVM, KNN e Redes Neurais -> exigem padronização.

Compreender o comportamento do conjunto de dados evita escolhas inadequadas.

## Avaliar Interpretabilidade e Implementação

Nem sempre o modelo mais preciso é o melhor. É necessário considerar:

- **Interpretabilidade:** RF e XGBoost permitem explicar decisões via Feature Importance.
- **Velocidade de Treinamento:** RF é ideal para baseline; LightGBM é extremamente rápido.
- **Escalabilidade:** para milhões de amostras, XGBoost e LightGBM são preferíveis.

A escolha depende do equilíbrio entre explicabilidade, performance e custo computacional.

## Seguir um Regime de Teste (Benchmark)

Profissionais utilizam um fluxo comparativo:

1. **Modelo Baseline:** simples, rápido e confiável.  
   *Sugestão:* Random Forest ou Regressão Logística.

2. **Modelo de Alta Performance:**  
   *Sugestão:* XGBoost ou LightGBM.

3. **Modelos Avançados (se necessário):**  
   *Sugestão:* Redes Neurais (LSTM, MLP) ou ensembles.

Esse processo garante uma escolha racional e comparável entre algoritmos.

## Resumo Aplicado ao Cenário de Queimadas

- **Baseline ideal:** Random Forest (robusto, interpretável e eficiente em dados tabulares).  
- **Para maior precisão:** XGBoost ou LightGBM.  
- **Se houver forte dependência temporal:** LSTM ou modelos híbridos.

## Testes

Como já foi informado antes a base de tudo são os testes, no papel podemos ter uma coisa, mas na hora de criar o modelo pode sair algo completamente diferente. Temos diversos tipos de algoritmos livres para ser testados, então cabe a nós tratar nossos dados criar features relevantes e treinar modelos para fazer comparações entre entre eles e encontrar qual é o melhor para o problema em questão.

**Random Forest (Baseline)**

- **Como funciona:** árvores de decisão treinadas em subconjuntos amostrados dos dados.
- **Vantagens:** robustez, menos propenso a overfitting, fornece importâncias de features (interpretabilidade).
- **Uso no projeto:** baseline rápido e explicável; primeiro modelo para comparar métricas (AUC, precisão, recall por classe, F1).

**XGBoost (Melhor desempenho esperado)**

- **Como funciona:** soma de árvores sequenciais que corrigem erros residuais.
- **Vantagens:** geralmente máxima precisão em dados tabulares, bom controle de regularização.
- **Uso no projeto:** se Random Forest não atender requisitos de acurácia, treinar e ajustar XGBoost, usando validação cruzada e busca de hiperparâmetros (Bayesian/Randomized search).

Critério de escolha:
- Começar com Random Forest pela interpretabilidade e estabilidade.
- Migrar para XGBoost para ganhar performance quando necessário, acompanhando validação cuidadosa para evitar overfitting.

**Métricas e Validação**

- **Métricas principais:** AUC-ROC, Precision-Recall (especial atenção se dados desbalanceados), F1 para classe positiva (foco de queimada).
- **Validação temporal:** usar splits que respeitem a ordem temporal (time-series cross-validation) para evitar vazamento de informação.

**Setup Local com Docker e Poetry**

Arquivos essenciais no diretório raiz:

- `docker-compose.yml` — orquestração do `app` e `postgres`.
- `.env` — variáveis de ambiente.
- `Dockerfile` — imagem da aplicação Python.
- `pyproject.toml` — gerenciado por `poetry` com dependências do projeto.

**Passo a Passo**

Agora que já foi informado como deve funcionar o projeto e quais ferramentas seram utilizas temos que estruturar um passo a passo para sabermos o que tem que ser feito de acordo com os passo.

1. **Extração dos Dados:** os dados seram retirados do DBQueimadas da INPE no formato de CSV.  

2. **Armazenar os Dados no DB:** como vamos utilizar o postgress para armazenar os dados para não ter que ficar lidando com muitos arquivos CSV o proximo passo é criar um schema com pydantic para que seja possível passar os dados para o DB de uma forma mais eficiente e melhor tratada.

3. **Tratamento dos Dados:** agora que temos os dados salvos no nosso banco de dados podemos extrailos e transformalos em um DataFreme do pandas para que seja possível criar as features e fazer o treinamento e os testes de uma forma mais eficiente.

4. **Treinamento do Modelo:** com os dados salvos em um DataFreme e feito a criação das features podemos dar incio no treinamento do modelo. Essa parte tem que ser feito alguma pesquisas antes para entender como funciona o modelo e como funciona os hiperparamentros, para que seja possível criar um modelo eficiente com as quantidades de dados passados no treinamento.

5. **Testes do Modelo:** com o modelo treinado agora é hora de entender como o modelo se sai com dados que ele ainda não viu, buscando entender se ele entendeu os padrões da forma correta.

**Pontos importantes** 

Como estamos lidando com arquivos CSV as pessoas que iram desenvolver o projeto teem que ter os mesmo arquivos CSV com os mesmo dados.

**Coisas a serem entendidas** 

No inicio do projeto já será utilizado o dockercompose para levantar a aplicação python junto com o banco de dados, ou no começo será utilizado o dockercompose somente para levantar o banco de dados e no final do projeto implementar a aplicação para ser levantada junto com o banco de dados no dockercompose. 
