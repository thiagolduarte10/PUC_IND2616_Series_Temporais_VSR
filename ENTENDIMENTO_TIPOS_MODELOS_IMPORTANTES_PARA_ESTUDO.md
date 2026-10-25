# Modelos importantes para o estudo

## Ponto de partida
Este arquivo apresenta cinco candidatos iniciais, não uma escolha final.
Eles foram selecionados por serem coerentes com os conteúdos da disciplina: referências de comparação, suavização exponencial, ARIMA/SARIMA, regressão dinâmica e séries hierárquicas.
Antes de escolher qualquer um, será necessário conhecer a frequência, os períodos disponíveis, os valores ausentes, os atrasos de notificação e o comportamento das séries por local.
O objetivo é começar com métodos interpretáveis e testar se eles funcionam em semanas ainda não observadas.

## Como ler as fichas
Cada ficha responde às mesmas perguntas: ideia central, funcionamento, situação adequada, exemplo, vantagens, limites, verificações e comparação.
O exemplo é ilustrativo: não representa um resultado obtido nem pressupõe que o padrão estará presente nos dados reais.
Como apoio conceitual, a disciplina usa a abordagem de previsão apresentada em [Forecasting: Principles and Practice](https://otexts.com/fpp3/).

---

## 1. Ingênuo sazonal (Seasonal Naive)

**O que é**
É uma referência simples que repete o valor observado no mesmo período sazonal anterior.
Em uma série semanal com sazonalidade anual, a previsão para uma semana usa o valor da semana equivalente do ano anterior.

**Como funciona**
Não procura tendência, relações causais ou formato matemático complexo.
Ele parte da hipótese mínima de que o padrão daquela semana tende a se repetir de um ciclo anual para o outro.

**Quando faz sentido**
É apropriado quando há um ciclo anual reconhecível e a pergunta é de curto prazo.
Também é indispensável como linha de base, mesmo que a série pareça simples ou irregular.

**Exemplo no estudo**
Se uma UF registrou 18 internações associadas ao VSR na semana epidemiológica 22 de 2025, a referência prevê 18 para a semana 22 de 2026.
Esse número é apenas um exemplo didático; o dado real pode ser diferente e pode sofrer atraso de registro.

**Pontos fortes**
É transparente, rápido e difícil de superar quando a sazonalidade é muito estável.
Por isso ele impede que um método mais sofisticado seja aceito apenas por parecer mais moderno.

**Cuidados e limites**
Ele ignora mudanças recentes, tendências, choques e diferenças entre anos.
Também pode falhar se a data e a intensidade do pico variarem de uma temporada para outra.

**O que verificar nos dados**
Precisamos confirmar se as séries semanais têm ciclos anuais comparáveis e se há semanas finais incompletas.
Também será preciso decidir como tratar semanas sem registro ou com notificação tardia.

**Como avaliar**
Ele será comparado com os demais em várias origens temporais, sempre prevendo semanas que ainda não estavam disponíveis no momento da previsão.
Se outro candidato não for consistentemente melhor, esta referência continua sendo a escolha mais honesta.

---

## 2. Suavização exponencial sazonal (ETS / Holt-Winters)

**O que é**
É uma família de modelos que descreve uma série por componentes de nível, tendência e sazonalidade.
ETS significa Error, Trend e Seasonal: erro, tendência e componente sazonal.

**Como funciona**
O método dá mais peso às observações recentes, sem descartar completamente o histórico.
Dependendo do comportamento observado, pode incluir ou não tendência e sazonalidade, em formas aditivas ou multiplicativas.

**Quando faz sentido**
É indicado quando a série apresenta padrão repetitivo, mas o nível e a intensidade variam gradualmente ao longo do tempo.
Costuma ser uma opção forte para séries curtas ou médias, desde que haja dados suficientes para identificar o ciclo.

**Exemplo no estudo**
Imagine uma UF em que o período de maior ocorrência costuma acontecer no meio do ano, mas o total anual cresce ou diminui aos poucos.
Um ETS sazonal atualiza esse padrão a cada nova semana e projeta as semanas seguintes a partir das componentes atualizadas.

**Pontos fortes**
É interpretável: podemos discutir separadamente o nível atual, uma possível tendência e a sazonalidade.
Também fornece previsões e intervalos de incerteza de forma natural no conjunto de modelos da disciplina.

**Cuidados e limites**
Ele pressupõe que as mudanças sejam relativamente graduais e pode reagir mal a quebras bruscas de padrão.
Para contagens muito baixas, muitos zeros ou sazonalidade instável, a configuração escolhida deve ser examinada com cautela.

**O que verificar nos dados**
Precisamos observar gráficos semanais, tendência, repetição de picos, dispersão e estabilidade da amplitude sazonal.
Também será necessário verificar se a série possui histórico suficiente para estimar uma sazonalidade anual confiável.

**Como avaliar**
Testaremos variantes com e sem tendência e com diferentes formas de sazonalidade, sem escolher pelo ajuste visual apenas.
A decisão dependerá do desempenho fora da amostra e da qualidade dos intervalos previstos.

---

## 3. SARIMA (ARIMA sazonal)

**O que é**
SARIMA é uma extensão sazonal da família ARIMA para séries com dependência entre observações próximas e entre ciclos anuais.
Ele combina diferenças, termos autorregressivos e termos de médias móveis nos níveis regular e sazonal.

**Como funciona**
O modelo pode remover tendências e padrões sazonais por diferenciação antes de representar a dependência restante.
Depois, usa o comportamento recente dos erros e valores passados para produzir previsões futuras.

**Quando faz sentido**
É adequado quando a série apresenta autocorrelação clara e uma sazonalidade que pode ser capturada de modo consistente.
É especialmente útil como alternativa ao ETS, pois descreve o histórico por uma lógica diferente.

**Exemplo no estudo**
Suponha que, após considerar o ciclo anual, o número de registros de uma semana ainda dependa fortemente das duas ou três semanas anteriores.
Um SARIMA pode representar essa memória curta e o efeito da repetição anual ao mesmo tempo.

**Pontos fortes**
Possui diagnóstico estatístico bem estabelecido, com análise de autocorrelação e resíduos.
Permite verificar se ainda resta estrutura não explicada depois do ajuste, em vez de confiar somente no erro médio.

**Cuidados e limites**
Requer atenção à estacionariedade, à escolha de diferenciações e à parcimônia dos parâmetros.
Uma especificação excessivamente complexa pode ajustar o passado muito bem e prever mal semanas futuras.

**O que verificar nos dados**
Será necessário examinar gráficos, ACF, PACF, diferenciações possíveis e testes de diagnóstico dos resíduos.
Também precisaremos confirmar se 52 semanas é um período sazonal viável para cada série disponível.

**Como avaliar**
Modelos SARIMA serão comparados por validação temporal e diagnósticos de resíduos, não apenas por AICc.
Uma boa escolha deve ter desempenho futuro competitivo e resíduos sem dependência relevante remanescente.

---

## 4. Regressão dinâmica com erros ARIMA (ARIMAX)

**O que é**
É uma regressão que inclui variáveis externas relevantes e trata a dependência temporal que sobra nos erros com um modelo ARIMA.
Quando há sazonalidade, ela também pode ser representada na parte de regressão ou nos erros.

**Como funciona**
Primeiro, o modelo relaciona a série de internações a informações observadas ao longo do tempo.
Depois, em vez de assumir que os erros são independentes, ele modela a memória temporal que permaneceu nesses erros.

**Quando faz sentido**
Só deve ser usado se existirem variáveis externas confiáveis, disponíveis no momento real da previsão e justificadas epidemiologicamente.
Ele não é obrigatório: se não houver covariáveis adequadas, a comparação deve ficar limitada aos modelos univariados.

**Exemplo no estudo**
Se fosse demonstrado que uma variável climática ou de vigilância melhora a previsão e está disponível sem atraso, ela poderia entrar como explicativa.
Por exemplo, o modelo poderia usar uma medida semanal conhecida até a data de corte, sem utilizar informação futura que não estaria disponível na prática.

**Pontos fortes**
Pode incorporar informação que a própria série de internações ainda não capturou.
Também torna explícito quais dados adicionais estão contribuindo para a estimativa, favorecendo discussão e auditoria.

**Cuidados e limites**
Uma associação histórica não prova causalidade nem garante ganho de previsão.
Há risco de vazamento de informação se uma variável só é divulgada depois da semana que se deseja prever.

**O que verificar nos dados**
Precisamos verificar origem, frequência, qualidade, atraso de divulgação e estabilidade de cada possível variável externa.
Também é necessário definir como prever a própria covariável para horizontes futuros, quando ela não estiver disponível.

**Como avaliar**
Ele só deve permanecer no conjunto se superar modelos sem covariáveis em validação temporal justa.
O ganho precisa compensar a maior complexidade, a dependência de novas fontes e o risco operacional.

---

## 5. Previsão hierárquica com reconciliação

**O que é**
Não é um modelo isolado de geração de previsões, mas uma estratégia para garantir coerência entre níveis geográficos.
Ela é importante aqui porque as previsões por UF devem ser compatíveis com os totais regionais e nacionais.

**Como funciona**
Primeiro são geradas previsões para cada nível ou apenas para os níveis mais detalhados.
Depois, essas previsões são combinadas ou ajustadas para que a soma das UFs forme a região e a soma das regiões forme o Brasil.

**Quando faz sentido**
Faz sentido sempre que houver interesse simultâneo em decisões locais, regionais e nacionais.
Ela pode ser aplicada sobre diferentes modelos-base, como ingênuo sazonal, ETS ou SARIMA.

**Exemplo no estudo**
Se a soma das previsões estaduais do Sudeste for 110 e a previsão regional independente for 95, existe incoerência.
A reconciliação busca uma previsão final que respeite a estrutura geográfica sem ignorar inteiramente a informação de cada nível.

**Pontos fortes**
Evita relatórios contraditórios entre painéis estaduais, regionais e nacionais.
Também permite avaliar se o nível agregado, que costuma ser menos ruidoso, ajuda a estabilizar previsões de UFs com poucos registros.

**Cuidados e limites**
Ela não corrige erros na definição do evento, atrasos de notificação ou escolhas ruins dos modelos-base.
Além disso, uma estratégia de reconciliação deve ser avaliada; coerência contábil não garante necessariamente menor erro.

**O que verificar nos dados**
Precisamos confirmar a correspondência entre UF, região e Brasil, além de checar se todos os totais são formados pela mesma regra de filtragem.
Também será necessário identificar se há mudanças territoriais, registros desconhecidos ou duplicidades que quebrem a soma.

**Como avaliar**
Compararemos previsões coerentes e não reconciliadas no mesmo período de validação, em todos os níveis geográficos.
A estratégia será mantida se preservar a coerência e melhorar ou, ao menos, não piorar materialmente a utilidade da previsão.

---

## Ordem inicial de estudo
Começaremos pelo ingênuo sazonal, ETS e SARIMA, pois usam apenas o histórico da própria série e permitem uma comparação transparente.
ARIMAX só entra se surgirem covariáveis defensáveis e disponíveis no tempo correto.
A previsão hierárquica será considerada quando as séries por UF, região e Brasil estiverem organizadas e validadas.
O resultado não será escolhido por sofisticação: vencerá o método que demonstre utilidade em semanas futuras e comunique sua incerteza com clareza.

---

## Glossário essencial

- **Série temporal:** valores observados em sequência no tempo, como o total semanal de internações.
- **Observação:** um valor individual da série; neste estudo, por exemplo, a contagem de uma UF em uma semana.
- **Frequência:** intervalo entre observações; aqui, a frequência planejada é semanal.
- **Granularidade:** nível de detalhe do dado, como semana, UF, região ou Brasil.
- **Tendência:** movimento persistente de crescimento, queda ou estabilidade ao longo de muitos períodos.
- **Sazonalidade:** padrão que tende a se repetir em determinados momentos do calendário, como ao longo do ano.
- **Ruído:** variação aleatória que não representa um padrão persistente ou previsível.
- **Autocorrelação:** relação entre o valor atual da série e seus próprios valores passados.
- **Estacionariedade:** situação em que as propriedades básicas da série se mantêm relativamente estáveis ao longo do tempo.
- **Horizonte de previsão:** quantas semanas à frente se deseja estimar.
- **Linha de base:** método simples usado como referência obrigatória para avaliar se modelos mais complexos realmente agregam valor.
- **Validação temporal:** avaliação que respeita a ordem dos acontecimentos, prevendo apenas períodos que ainda não eram conhecidos.
- **Fora da amostra:** dados futuros que não foram usados para ajustar o modelo e servem para testar sua capacidade real de previsão.
- **Sobreajuste:** quando o método aprende detalhes acidentais do passado, mas tem baixo desempenho em semanas futuras.
- **Intervalo de previsão:** faixa que expressa a incerteza em torno de uma estimativa, e não apenas um valor único.
- **Covariável:** informação adicional que pode ajudar a previsão, desde que esteja disponível no momento correto.
- **Atraso de notificação:** diferença entre a ocorrência do evento e sua entrada completa no sistema de vigilância.
- **Vazamento de informação:** uso indevido de dados do futuro durante o ajuste ou a avaliação de uma previsão.
- **Série hierárquica:** conjunto de séries com níveis que se somam, como UFs, regiões e Brasil.
- **Reconciliação:** ajuste das previsões para que os totais de UFs, regiões e Brasil permaneçam coerentes entre si.
