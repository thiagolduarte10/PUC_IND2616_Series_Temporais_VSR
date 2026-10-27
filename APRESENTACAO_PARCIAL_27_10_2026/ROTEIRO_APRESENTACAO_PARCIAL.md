# Roteiro da apresentação parcial — VSR e Séries Temporais

**Duração planejada:** 5 a 7 minutos.  
**Uso:** apresente as ideias em linguagem natural. Os números e os gráficos ficam na tela como apoio, sem a necessidade de ler cada item.

## 1. Capa — 25 a 35 segundos

“Boa tarde. Nós somos Thiago Paes, Joan Souza, Matheus Accioly e Isabelle Gagno. Este é o nosso trabalho para a disciplina IND2616, Séries Temporais, ministrada pelo professor Fernando Cyrino, no Mestrado da PUC-Rio.

Nosso tema é a previsão de internações por vírus sincicial respiratório, o VSR, em crianças menores de dois anos. A pergunta central é simples: usando o histórico semanal, conseguimos antecipar a demanda hospitalar antes dos períodos de maior circulação do vírus?”

## 2. Problema e dados — 55 a 70 segundos

“O objetivo não é explicar todas as causas da doença. Fatores como vacinação, clima, testagem e acesso à assistência também podem influenciar os registros. Nosso foco é mais específico: estimar quantas internações podem ocorrer nas próximas semanas, para apoiar o planejamento de leitos pediátricos, equipes e insumos.

Usamos os microdados públicos do SIVEP-Gripe, disponíveis no OpenDataSUS, de 2019 a 2026. Partimos de cerca de 4,68 milhões de registros de SRAG. Aplicamos um recorte claro: internação por SRAG, criança menor de dois anos, confirmação de VSR por PCR ou antígeno, UF de residência válida e data de início dos sintomas disponível.

Depois desse processo, ficamos com 158.358 notificações únicas. Transformamos esses registros individuais em contagens semanais por UF, região e Brasil.”

## 3. Tratamento e semanas maduras — 50 a 65 segundos

“Antes de qualquer modelo, verificamos a qualidade da base: campos, datas, códigos laboratoriais e duplicidades. Encontramos dois pares de registros duplicados. Não apagamos linhas de forma automática: auditamos os casos e aplicamos uma regra temporal documentada para preservar uma única versão coerente de cada notificação.

Também usamos o conceito de semanas maduras. Uma internação com sintomas em uma semana pode ser notificada ou confirmada posteriormente. Assim, as semanas mais recentes ainda parecem incompletas. Adotamos uma janela conservadora de 13 semanas e usamos 395 semanas maduras como histórico de análise. Isso reduz o risco de ensinar o modelo com um falso sinal de queda nos registros.”

## 4. O que a análise exploratória mostrou — 75 a 95 segundos

“A análise exploratória mostrou um padrão sazonal: no Brasil, os picos de VSR aparecem aproximadamente entre as semanas epidemiológicas 11 e 19, em torno de março a maio. Mas as regiões não seguem exatamente o mesmo calendário. Sudeste e Centro-Oeste apresentaram um comportamento relativamente mais precoce e concentrado; o Nordeste teve picos mais tardios em anos recentes.

Também identificamos mudança de nível e de variabilidade. A média semanal brasileira foi de aproximadamente 288 casos em 2022 e 830 em 2025. O desvio-padrão também aumentou, de cerca de 174 para 912. Em termos simples, além de observarmos mais casos, observamos ondas mais oscilantes.

Nas UFs, há outra diferença importante: treze estados tiveram mais de metade das semanas sem casos registrados. Isso não significa que o trabalho esteja errado. Significa que algumas séries são esparsas e exigem mais cautela. Por isso, Brasil e regiões serão a primeira base para a comparação dos modelos, e as UFs serão analisadas de acordo com seu volume e intermitência.”

## 5. Modelos candidatos — 45 a 60 segundos

“A próxima etapa é a modelagem. Vamos começar por referências simples, principalmente o ingênuo sazonal. Ele usa como previsão a semana epidemiológica equivalente da temporada anterior. Se um modelo mais sofisticado não superar essa referência de forma consistente, ele não acrescenta valor prático.

Depois compararemos ETS ou Holt-Winters, que representa nível, tendência e sazonalidade; SARIMA, que representa dependência temporal e ciclo anual; e abordagens hierárquicas, porque os dados têm a estrutura UF, região e Brasil.”

## 6. Avaliação e encerramento — 55 a 70 segundos

“A avaliação respeitará a ordem do tempo. Não faremos uma divisão aleatória entre treino e teste, porque isso poderia usar futuro para prever passado. Em vez disso, simularemos diversas datas históricas: o modelo verá somente as semanas disponíveis até cada corte e fará previsões para uma, quatro, oito e treze semanas à frente.

Teremos 58 cortes temporais por série, com uma janela de treino que cresce ao longo do tempo. Vamos usar MAE, que informa o erro médio em número de casos; RMSE, que dá mais peso a erros grandes; e MASE, que ajuda a comparar séries de escalas diferentes.

Em resumo, já temos uma base tratada e auditável, evidência de sazonalidade e um protocolo justo de avaliação. Agora vamos testar quais modelos realmente antecipam melhor as internações por VSR. Obrigado.”

## Frases de transição, se necessário

- “Antes de prever, precisávamos garantir que a série medisse o fenômeno correto.”
- “A análise exploratória não escolhe o vencedor, mas define as características que os modelos precisam representar.”
- “Sazonalidade é uma repetição aproximada: o período de pico retorna, mas não com a mesma intensidade todos os anos.”
- “A escolha final será feita pelo desempenho fora da amostra, e não pela complexidade do modelo.”
