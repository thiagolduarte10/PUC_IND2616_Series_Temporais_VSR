# Guia detalhado da apresentação parcial — VSR e Séries Temporais

Este documento complementa o roteiro falado. Use-o para estudar os termos, responder perguntas e evitar afirmações além do que os dados permitem demonstrar.

## Mapa da apresentação

| Bloco HTML | Ideia central | Tempo sugerido |
|---|---|---:|
| Capa | Pergunta e relevância | 1 min |
| Problema | O que queremos prever e por quê | 1 min |
| Dados | Fonte, recorte e unidade de análise | 2 min |
| Tratamento | Por que a série é confiável para a próxima etapa | 2 min |
| Exploração | Sazonalidade, região, nível e variabilidade | 3 min |
| Modelos | Candidatos e referência sazonal | 2 min |
| Validação | Como evitar vazamento e comparar justamente | 2 min |
| Fechamento | O que foi entregue e o próximo passo | 30 s |

## Termos fundamentais

### Recorte de dados

É o conjunto de regras que seleciona os registros compatíveis com a pergunta de pesquisa. Não é uma exclusão arbitrária: sem ele, a série poderia misturar idades, doenças respiratórias, casos sem confirmação laboratorial e notificações sem relação com internação.

No trabalho, o recorte inclui SRAG hospitalizada, crianças menores de dois anos, VSR confirmado por PCR ou antígeno, UF de residência válida e data de início dos sintomas disponível.

### Semana epidemiológica

É uma unidade de sete dias usada para organizar a vigilância de doenças. No painel, a semana começa no domingo. O ano epidemiológico é definido pela quinta-feira daquela semana, seguindo a convenção ISO usada no código.

Alguns anos possuem 53 semanas. Isso depende do alinhamento do calendário, não de o ano ser bissexto. Por exemplo, 2020 teve 53 semanas e 2022 teve 52; 2024 foi bissexto e também teve 52 semanas.

### Semana madura

É uma semana cuja informação teve tempo suficiente para ser completada no sistema. O caso pode ocorrer em uma data, mas ser digitado ou confirmado laboratorialmente depois. Portanto, as semanas muito recentes normalmente sofrem sub-registro temporário.

O estudo adotou 13 semanas de maturação, uma margem conservadora baseada na análise de atrasos de disponibilidade. As 395 semanas maduras são adequadas para análise histórica e validação; as 12 semanas posteriores permanecem no painel, mas não entram como verdade final da avaliação.

### Duplicidade e sua resolução

Duplicidade acontece quando uma mesma notificação aparece mais de uma vez. Ela pode inflar artificialmente a contagem semanal e criar picos inexistentes.

Foram encontrados dois pares com o mesmo identificador de notificação e informações temporais conflitantes. Cada caso foi auditado. A escolha priorizou a versão com menor atraso não negativo entre início dos sintomas e notificação; em empate, foram usadas regras documentadas envolvendo a data de digitação e o arquivo mais recente. O resultado final contém 158.358 notificações únicas.

### Painel semanal

É a tabela pronta para séries temporais. Cada linha representa uma unidade geográfica em uma semana: uma UF, uma região ou o Brasil. O valor principal é o número de casos confirmados de VSR naquela semana.

O painel possui 27 UFs, 5 regiões e Brasil, com 407 semanas no total. A soma das UFs foi conferida contra os totais regionais e nacionais.

## Como explicar os achados exploratórios

### Sazonalidade

Sazonalidade é uma variação que tende a se repetir em intervalos regulares. Aqui, o intervalo de interesse é aproximadamente anual. O Brasil apresentou picos principalmente entre as semanas 11 e 19.

Evite dizer que “todo ano é igual”. A mensagem correta é: há um padrão recorrente, mas a intensidade e a semana exata do pico variam entre anos e regiões.

### Padrão precoce e concentrado

Um padrão precoce é aquele cujo aumento e pico surgem mais cedo no calendário epidemiológico. Um padrão concentrado tem subida, pico e queda reunidos em uma janela menor de semanas.

Na análise, Sudeste e Centro-Oeste foram relativamente mais precoces e concentrados. O Nordeste apresentou picos mais tardios em anos recentes. Isso justifica não impor um único calendário de risco, rígido e nacional, a todas as regiões.

### Média semanal

É a soma dos casos de uma temporada dividida pela quantidade de semanas daquela temporada. Ela ajuda a comparar anos que podem ter números diferentes de semanas, como 2020, que teve 53.

Exemplo: em 2022, o Brasil teve média de 287,9 casos por semana; em 2025, 829,8. A leitura é que a altura típica da série aumentou, não apenas o total acumulado.

### Desvio-padrão, nível e variabilidade

O **nível** é a faixa típica da série. Uma série cujo nível cresce passa a registrar, em geral, mais casos mesmo fora do pico.

O **desvio-padrão** mede o quanto os valores se afastam da média. Um desvio-padrão maior significa oscilação maior. Em 2022, o Brasil teve desvio-padrão semanal de 173,7; em 2025, 912,3.

Quando média e desvio-padrão sobem juntos, dizemos que há indício de variabilidade dependente do nível. Isso também é chamado de heterocedasticidade em linguagem estatística. Não significa que há erro nos dados: significa que picos maiores são acompanhados por oscilações maiores.

Na apresentação, prefira dizer “variabilidade” a “incerteza” ao descrever esse gráfico. Incerteza formal de previsão exige intervalos preditivos, que serão estudados na modelagem. O gráfico atual mostra variabilidade histórica observada.

### Autocorrelação

Autocorrelação é a correlação da série com ela mesma após um deslocamento no tempo. Uma autocorrelação de 0,987 na defasagem de uma semana significa forte semelhança entre semanas consecutivas do histórico brasileiro.

Valores altos em 52 e 53 semanas sugerem repetição anual. Valores negativos próximos de 26 semanas são compatíveis com a oposição entre a parte alta e a parte baixa do ciclo anual.

Isso não prova que a série é estacionária. Pelo contrário: a mudança de nível e variabilidade mostra que ainda precisaremos de diagnósticos depois do ajuste dos modelos.

## Como explicar os modelos sem prometer resultado antes do teste

### Referência ingênua

O método ingênuo simples prevê que o próximo valor será igual ao último valor observado. É uma referência mínima de persistência.

### Ingênuo sazonal

Prevê a semana futura com base na semana correspondente de aproximadamente um ano antes:

`ŷ(t+h) = y(t+h−52)`

Ele é obrigatório como referência porque os dados têm ciclo anual. Um método sofisticado que não o supera de forma consistente não oferece ganho prático demonstrado.

### ETS ou Holt-Winters

É uma família que atualiza componentes de nível, tendência e sazonalidade conforme novas semanas chegam. Pode funcionar bem quando o ciclo é forte e a evolução dos componentes é gradual.

### SARIMA

É uma extensão sazonal de ARIMA. Ela usa valores passados e erros passados para representar dependência temporal, além de incorporar a periodicidade anual. É coerente com a autocorrelação observada, mas ainda precisa ser ajustada e validada.

### Regressão dinâmica / ARIMAX

Inclui variáveis externas, como clima, vacinação ou indicadores de circulação viral, junto de um erro temporal. Só deve ser usada se a covariável tiver qualidade, disponibilidade na data da previsão e justificativa epidemiológica. Neste momento, ela é uma candidata, não uma solução garantida.

### Modelos hierárquicos

Os dados possuem níveis geográficos aninhados: UFs compõem regiões e regiões compõem o Brasil. Métodos hierárquicos buscam manter coerência entre essas previsões. Por exemplo, as previsões das UFs devem poder somar para a previsão regional correspondente.

## Validação temporal: a ideia central

### Por que não dividir os dados aleatoriamente?

Em classificação ou regressão comum, é frequente sortear linhas para treino e teste. Em uma série temporal isso é inadequado. Uma semana de 2025 no treino ajudaria a prever uma semana de 2022 no teste, o que seria impossível em uma previsão real.

Essa mistura de passado e futuro é chamada de vazamento de informação. Ela reduz artificialmente o erro e pode fazer um modelo ruim parecer bom.

### O que são cortes temporais?

Cada corte é uma simulação de uma data histórica de decisão. Por exemplo: fingimos estar em 19/12/2021, treinamos com as 156 semanas anteriores e prevemos 1, 4, 8 e 13 semanas futuras. Em seguida, comparamos as previsões com os valores observados que já conhecemos hoje.

Depois deslocamos o corte quatro semanas à frente e repetimos o processo. Foram definidos 58 cortes para cada série. O treino é expansivo: todo dado que já ocorreu pode entrar no treino seguinte, mas nenhuma observação futura entra antes da hora.

### Horizontes avaliados

- **1 semana:** acompanhamento imediato.
- **4 semanas:** aproximadamente um mês.
- **8 semanas:** aproximadamente dois meses.
- **13 semanas:** aproximadamente um trimestre.

É importante apresentar métricas separadas por horizonte. Um modelo pode ser excelente para uma semana e fraco para três meses.

## Métricas de erro

### MAE — Mean Absolute Error

Fórmula: `MAE = média(|observado − previsto|)`.

Interpretação: em média, quantos casos o modelo erra por previsão. É a métrica mais fácil de traduzir para planejamento. Se o MAE for 40, o erro típico é de aproximadamente 40 internações.

### RMSE — Root Mean Squared Error

Fórmula: `RMSE = raiz(média((observado − previsto)²))`.

Como o erro é elevado ao quadrado, erros grandes pesam mais. É útil porque errar muito em uma semana de pico pode ter impacto operacional maior que pequenos erros em semanas de baixa.

### MASE — Mean Absolute Scaled Error

O MASE divide o erro absoluto médio do modelo por uma escala de erro de referência calculada no treino. Isso permite comparar séries com tamanhos muito diferentes, como São Paulo e uma UF de baixo volume.

Em termos gerais, valor menor que 1 indica desempenho melhor que a referência usada na escala. Na etapa de modelagem, a definição exata da escala — simples ou sazonal — será explicitada antes do cálculo, para não haver ambiguidade.

### Por que MAPE não será a métrica principal?

O MAPE divide o erro pelo valor observado. Quando o observado é zero, ele fica indefinido ou explode. Como várias UFs têm muitas semanas com zero, o MAPE pode gerar conclusões enganosas.

## Limites que devem ser ditos com clareza

- Os dados mostram notificações registradas no SIVEP-Gripe; não representam necessariamente todos os casos de VSR existentes na população.
- O estudo é preditivo, não causal. Mudanças entre anos não podem ser atribuídas automaticamente a uma causa única.
- As semanas recentes não são usadas como verdade final porque podem sofrer atualização.
- Os gráficos exploratórios descrevem o passado; a capacidade de previsão só será demonstrada com validação temporal fora da amostra.
- A melhor técnica pode variar por horizonte e por nível geográfico.

## Perguntas prováveis e respostas curtas

**Por que menores de dois anos?**  
Porque é uma faixa etária pediátrica especialmente relevante para hospitalizações por VSR e cria um foco epidemiológico coerente para a série.

**Por que não usar apenas o Brasil?**  
Porque a dinâmica regional é diferente. O agregado nacional é útil, mas pode esconder diferenças de timing, volume e intermitência.

**Por que não usar todas as semanas de 2026?**  
Porque parte delas ainda pode receber notificações e confirmações. Usá-las como verdade final subestimaria artificialmente os casos recentes.

**Por que 13 semanas de maturação?**  
Porque a análise de atrasos mostrou que uma margem conservadora era necessária para reduzir o risco de avaliar semanas ainda incompletas.

**Por que testar modelo simples se existem modelos avançados?**  
Porque a complexidade só faz sentido se trouxer ganho preditivo real. A referência sazonal estabelece um padrão mínimo rigoroso.

**O trabalho já encontrou o melhor modelo?**  
Não. Até agora, estabelecemos a base, a exploração e o protocolo de avaliação. A próxima fase ajustará e comparará os modelos.
