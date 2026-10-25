# Roteiro da apresentação parcial — VSR e Séries Temporais

**Duração sugerida:** 10 a 15 minutos.  
**Tom recomendado:** explicar a lógica do trabalho antes dos detalhes técnicos. Não é necessário decorar; use este texto como guia.

## 1. Capa — cerca de 1 minuto

“Boa tarde. Nós somos Thiago Paes, Joan Souza, Matheus Accioly e Isabelle Gagno. Este é o nosso trabalho para a disciplina IND2616, Séries Temporais, ministrada pelo professor Fernando Cyrino, no Mestrado da PUC-Rio.

Nosso tema é a previsão de internações por vírus sincicial respiratório, o VSR, em crianças menores de dois anos no Brasil. Escolhemos esse problema porque o VSR apresenta ondas sazonais e pressiona a rede pediátrica em determinados períodos do ano.

A pergunta que orienta o estudo é: será que, usando o histórico semanal disponível, conseguimos antecipar quantas internações por VSR podem ocorrer nas próximas semanas?”

## 2. Problema proposto — cerca de 1 minuto

“O objetivo não é afirmar que um modelo explica todas as causas da doença. Existem vacinação, clima, acesso a testes, comportamento da população e muitos outros fatores que não estão todos na nossa base.

O foco é mais objetivo: construir previsões semanais que possam ajudar no planejamento. Se uma região recebe um aviso confiável de que as internações podem aumentar nas próximas quatro ou oito semanas, ela pode se preparar melhor para leitos pediátricos, equipes e insumos.

Por isso, nossa unidade principal não é o paciente individual. É a quantidade de internações confirmadas em cada semana.”

## 3. Dados usados — cerca de 2 minutos

“Usamos microdados públicos do SIVEP-Gripe, disponibilizados pelo OpenDataSUS. Os arquivos cobrem 2019 a 2026 e contêm notificações de Síndrome Respiratória Aguda Grave, ou SRAG.

Começamos com aproximadamente 4,68 milhões de registros brutos de SRAG. Mas o nosso estudo não usa todos esses registros. Nós definimos um **recorte de dados**, que é uma regra clara para decidir quais linhas realmente pertencem à pergunta do trabalho.

No nosso caso, o registro precisa atender simultaneamente a cinco critérios: ser uma internação por SRAG, envolver criança menor de dois anos, ter confirmação de VSR por PCR ou antígeno, possuir UF de residência válida e ter data de início dos sintomas disponível.

Depois desse recorte e das verificações de qualidade, chegamos a 158.358 notificações únicas. Em seguida, transformamos registros individuais em contagens semanais por Unidade da Federação, região e Brasil.

Usamos semanas epidemiológicas. Em vez de trabalhar apenas com meses, agrupamos os casos em blocos de sete dias. Isso é melhor para acompanhar uma onda de doença respiratória, que pode subir e cair dentro de um mesmo mês.”

## 4. Tratamento e limpeza dos dados — cerca de 2 minutos

“Antes de comparar modelos, foi necessário tratar a base. Isso significa conferir se os dados realmente representam o que acreditamos que representam.

Primeiro, verificamos os arquivos anuais e a estrutura das colunas. Depois aplicamos o recorte de idade, hospitalização, confirmação de VSR, local e data. Também verificamos campos ausentes, datas inválidas e códigos laboratoriais.

Um ponto importante foi resolver duplicidades. Duplicidade significa que a mesma notificação aparece mais de uma vez. Encontramos dois pares de registros com o mesmo identificador, mas com informações temporais diferentes entre versões de arquivos anuais. Nós não simplesmente apagamos uma linha: auditamos cada caso e aplicamos uma regra documentada para manter a versão temporalmente mais coerente.

Outra decisão importante envolve as semanas maduras. Uma notificação pode ser registrada ou confirmada depois da semana em que os sintomas começaram. Portanto, as semanas mais recentes parecem ter menos casos não necessariamente porque a circulação caiu, mas porque parte das informações ainda não chegou ao sistema.

Chamamos de semana madura uma semana que já teve tempo suficiente para receber a maior parte das atualizações. Usamos uma janela conservadora de 13 semanas. Assim, trabalhamos com 395 semanas maduras para entender o histórico e deixamos as 12 semanas mais recentes fora da avaliação.”

## 5. O que encontramos na análise exploratória — cerca de 3 minutos

“Depois da limpeza, fizemos a análise exploratória, ou seja, estudamos o comportamento da série antes de escolher modelos.

O primeiro achado é a sazonalidade. Sazonalidade significa que existe um padrão que tende a se repetir dentro do ano. No Brasil, os picos apareceram aproximadamente entre as semanas epidemiológicas 11 e 19, algo em torno de março a maio. Mas esse padrão não é idêntico em todas as regiões.

Quando dizemos que um padrão é mais precoce e concentrado, queremos dizer duas coisas. Precoce: o pico acontece mais cedo no ano. Concentrado: o período de aumento é mais curto e mais reunido em torno do pico. Sudeste e Centro-Oeste mostraram comportamento relativamente mais precoce e concentrado; o Nordeste apresentou picos mais tardios nos anos recentes.

Também observamos mudança de nível entre as temporadas. Nível é, em linguagem simples, a altura típica da série: se o número de casos passou a ficar, em geral, em uma faixa mais alta, dizemos que o nível aumentou. No Brasil, a média semanal foi de cerca de 288 casos em 2022 e de cerca de 830 em 2025.

Ao mesmo tempo, o desvio-padrão também aumentou. O desvio-padrão mede o quanto os valores oscilam ao redor da média. Em 2022, ele foi aproximadamente 174; em 2025, aproximadamente 912. Portanto, não apenas houve mais casos: as ondas passaram a oscilar mais.

Isso não prova uma causa específica. Pode haver mudanças epidemiológicas, de testagem, de vigilância ou de notificação. O que podemos afirmar é que o processo observado não ficou estável ao longo de todas as temporadas.”

## 6. Dependência temporal — cerca de 1 minuto

“Também medimos a autocorrelação. Autocorrelação é a relação entre a série e ela mesma em semanas diferentes.

Encontramos autocorrelação muito alta de uma semana para a seguinte, 0,987 no Brasil. Isso quer dizer que semanas próximas tendem a se parecer. Também encontramos valores altos em 52 e 53 semanas, o que reforça a repetição anual.

Essa descoberta ajuda a explicar por que modelos sazonais fazem sentido como candidatos. Mas ela não escolhe o vencedor antes do teste; ela apenas indica que os modelos devem conseguir representar memória de curto prazo e ciclo anual.”

## 7. Quais modelos serão testados — cerca de 2 minutos

“A partir daqui entramos na fase de modelagem. A primeira regra é não começar pelo modelo mais sofisticado. Primeiro vamos criar referências simples.

A principal referência será o ingênuo sazonal. Ele prevê que uma semana futura terá um comportamento parecido com a semana equivalente da temporada anterior. Em termos simples, para prever uma determinada semana, olhamos aproximadamente 52 semanas para trás.

Depois, vamos comparar essa referência com modelos estudados na disciplina: ETS ou Holt-Winters, que separa nível, tendência e sazonalidade; SARIMA, que representa dependência temporal e sazonalidade; regressão dinâmica, se surgirem covariáveis externas adequadas; e abordagens hierárquicas, porque nossos dados possuem a estrutura UF, região e Brasil.

O ponto central é: um modelo mais complexo só será útil se superar uma referência simples de forma consistente.”

## 8. Como os modelos serão avaliados — cerca de 2 minutos

“Para não misturar passado e futuro, não vamos separar os dados aleatoriamente, como é comum em outros tipos de análise.

Em séries temporais, uma separação aleatória criaria vazamento de informação: o modelo poderia usar dados de uma semana futura para ajudar a prever uma semana passada. Isso faria o resultado parecer melhor do que seria no mundo real.

Por isso, criamos cortes temporais. Um corte temporal é como voltar no tempo e fingir que estamos em uma data específica. Treinamos o modelo somente com o que seria conhecido até aquela data e pedimos uma previsão para uma, quatro, oito ou treze semanas à frente. Depois comparamos a previsão com o valor que realmente ocorreu.

Criamos 58 cortes para cada série. O treino começa com três anos de histórico e cresce ao longo do tempo. Assim, testamos os modelos em períodos de baixa, subida, pico e queda.

Usaremos MAE, RMSE e MASE. O MAE é o erro absoluto médio: em média, quantos casos o modelo errou. O RMSE dá peso maior a erros grandes, sendo importante porque errar durante um pico pode ser mais grave. O MASE coloca o erro em uma escala comparável com uma referência simples, permitindo comparar séries de tamanhos diferentes.

Evitaremos MAPE como métrica principal porque ele se comporta mal quando o valor observado é zero, algo frequente em várias UFs.”

## 9. Fechamento — cerca de 30 segundos

“Em resumo, já construímos a base de forma auditável, identificamos sazonalidade, diferenças regionais, aumento de nível e variabilidade e definimos uma validação temporal justa.

Agora a próxima etapa é medir, com esse mesmo protocolo, quais modelos realmente acrescentam valor em relação ao ingênuo sazonal. O resultado que buscamos é uma previsão útil e interpretável para antecipar a demanda por internações pediátricas por VSR. Obrigado.”

## Frases úteis para transição

- “Antes de prever, precisamos ter certeza de que a série mede o fenômeno correto.”
- “A análise exploratória não escolhe o modelo; ela define quais características ele precisa respeitar.”
- “Sazonalidade não significa repetição perfeita: o pico se repete, mas sua intensidade e semana exata variam.”
- “O modelo será escolhido por desempenho fora da amostra, não por aparência ou complexidade.”
