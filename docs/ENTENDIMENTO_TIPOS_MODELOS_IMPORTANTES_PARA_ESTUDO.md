# Modelos importantes para o estudo — guia atualizado após a execução

Atualização em 14/11/2026: as fichas 1–5 descrevem a rodada clássica até a etapa 40. As fichas 6–8 e a política vigente ao final incorporam as etapas 41–43. Quando uma ficha antiga diz “final”, refere-se à primeira rodada.

## Propósito deste documento

Este arquivo começou como um mapa de candidatos antes de conhecermos os dados. Agora ele registra o que cada família de modelos significa, como foi usada no trabalho e qual foi sua contribuição real para prever semanalmente internações por SRAG associada ao VSR em crianças menores de dois anos.

O estudo trabalhou com 395 semanas maduras, de 30/12/2018 a 19/07/2026, e com uma hierarquia geográfica de 27 UFs, cinco regiões e Brasil. As previsões foram avaliadas em 58 origens temporais e nos horizontes de 1, 4, 8 e 13 semanas. Portanto, as conclusões abaixo decorrem de previsão fora da amostra, e não de ajuste visual ao passado.

## Resultado da primeira rodada (etapas 1–40)

| Método ou estratégia | Foi testado? | Papel final no trabalho |
|---|---|---|
| Ingênuo | Sim | Melhor referência curta para UFs; usado na Base V2 em 1 e 4 semanas. |
| Ingênuo sazonal | Sim | Melhor referência em 8 e 13 semanas; mantido na política final. |
| ETS amortecido | Sim | Melhor escolha não hierárquica para Brasil e regiões em 1 e 4 semanas. |
| SARIMA clássico | Sim | Não atingiu cobertura estável suficiente; não entrou no ranking final. |
| SARIMAX com harmônicos | Sim | Convergiu, mas não superou as escolhas selecionadas. |
| Bottom-up, top-down e WLS estrutural | Sim | Foram comparadores hierárquicos; não foram escolhidos como política final. |
| MinT com shrinkage OAS | Sim | Válido como comparador, mas gerou previsões negativas sem restrição. |
| MinT não negativo | Sim | Política final em 1 e 4 semanas quando é preciso comunicar toda a hierarquia. |

## Como interpretar uma comparação de modelos

Um método não é “bom” por ter fórmula mais complexa. Ele precisa prever semanas que ainda não estavam disponíveis, produzir resultados em todos os cortes exigidos e respeitar o uso pretendido. Neste trabalho, foram considerados ao mesmo tempo:

- **MAE:** erro absoluto médio em número de internações;
- **RMSE:** erro quadrático médio, mais sensível a erros grandes;
- **MASE:** erro escalonado que permite comparar Brasil, regiões e UFs;
- **cobertura:** quantidade de previsões efetivamente concluídas;
- **não negatividade:** uma contagem prevista não pode ser menor que zero;
- **coerência hierárquica:** UFs devem somar para região e regiões devem somar para Brasil.

Assim, o menor erro médio isolado não foi o único critério. Uma previsão impossível ou incompatível com os outros níveis geográficos não é operacionalmente adequada para comunicar demanda de internações.

---

## 1. Referências ingênuas: persistência e sazonalidade

### Ideia central

Uma referência ingênua não tenta descobrir uma estrutura sofisticada. Ela transforma uma regra simples em previsão e estabelece o mínimo que modelos mais complexos precisam superar.

O **ingênuo** repete o último valor observado:

\[
\hat{y}_{t+h} = y_t
\]

O **ingênuo sazonal** repete o valor do ciclo anual anterior. Para séries semanais, a referência corresponde aproximadamente à mesma semana da temporada anterior:

\[
\hat{y}_{t+h} = y_{t+h-m}, \quad m \approx 52
\]

### Por que fez sentido neste estudo

As séries de Brasil e regiões têm grande autocorrelação de curto prazo e repetição anual. Já muitas UFs são intermitentes: 13 têm mais de 50% das semanas maduras sem casos. Nessas séries, uma regra simples pode ser mais estável do que um modelo que tente estimar tendência e sazonalidade local com poucos eventos.

### Como foi avaliado

As duas referências foram aplicadas nas mesmas 58 origens expansivas e nos mesmos horizontes usados pelos demais modelos. Não receberam informação futura nem foram tratadas como meros exemplos didáticos.

### Resultado observado

Para Brasil e regiões, o ingênuo é uma referência forte no curtíssimo prazo, mas o ETS amortecido foi melhor em 1 e 4 semanas. Em 8 e 13 semanas, o ingênuo sazonal foi difícil de superar: obteve MASE médio de 1,741 e 1,823, respectivamente.

Nas UFs, a comparação mostrou um padrão ainda mais claro. Em 1 semana, o ingênuo teve MASE 1,145 contra 2,296 do ingênuo sazonal e venceu nas 27 UFs. Em 4 semanas, venceu em 22 das 27 UFs. Em 8 e 13 semanas, o sazonal voltou a ser melhor em 25 e 27 UFs, respectivamente.

### Decisão final

As referências não foram descartadas por serem simples. Elas formam a Base V2:

- **UFs em 1 e 4 semanas:** ingênuo;
- **UFs em 8 e 13 semanas:** ingênuo sazonal;
- **Brasil e regiões em 8 e 13 semanas:** ingênuo sazonal.

### Ponto de aprendizagem

Um baseline não é um modelo “fraco”. Quando ele vence, a conclusão científica é que o conjunto de dados ainda não demonstrou ganho suficiente para justificar uma solução mais complexa naquele horizonte.

---

## 2. ETS com tendência amortecida

### Ideia central

ETS é uma família de suavização exponencial que descreve a série por componentes de erro, nível, tendência e sazonalidade. A versão adotada usa tendência amortecida: ela permite movimento recente de crescimento ou queda, mas evita prolongar indefinidamente uma tendência como se ela fosse permanente.

De forma intuitiva, o modelo atualiza continuamente seu entendimento de:

- qual é o nível atual de internações;
- se há movimento recente de alta ou baixa;
- como o padrão anual se repete;
- quanto os dados recentes devem pesar em relação ao histórico.

### Por que fez sentido neste estudo

Brasil e regiões têm séries densas, com sazonalidade anual forte, mas com mudanças no nível e na amplitude entre temporadas. Esse é justamente o cenário em que um ETS pode ser útil: há informação suficiente para aprender o ciclo, mas não é desejável assumir tendência linear indefinida.

### Desafio encontrado

A primeira tentativa ETS apresentou avisos e falhas de convergência em parte dos ajustes. Isso não foi ignorado. A Etapa 23B aplicou uma inicialização sazonal heurística, mantendo a mesma tarefa e a mesma estrutura de previsão. Com a inicialização robusta, os 348 ajustes previstos convergiram.

Convergir não significa automaticamente prever melhor. Significa que a solução numérica foi obtida de modo estável e pode ser comparada justamente com as referências.

### Resultado observado

ETS amortecido foi a melhor escolha não hierárquica em curto prazo para Brasil e regiões. Seu MASE médio foi 0,507 em 1 semana e 1,311 em 4 semanas, superando as referências utilizadas nessa comparação. Em 8 e 13 semanas, porém, o ingênuo sazonal foi mais robusto.

### Decisão final

ETS amortecido entra na Base V2 para:

- **Brasil em 1 e 4 semanas**;
- **cinco regiões em 1 e 4 semanas**.

Ele não foi forçado nos horizontes de 8 e 13 semanas, porque a evidência observada favoreceu a referência sazonal.

### Limites importantes

ETS não explica causalmente as internações. Ele resume padrões da própria série. Também não é indicado como solução única para UFs intermitentes, pois muitas delas não têm sinal local contínuo suficiente para estimar componentes sazonais com a mesma estabilidade dos agregados.

---

## 3. SARIMA: tentativa de modelar a dependência temporal sazonal

### Ideia central

SARIMA estende a família ARIMA para capturar dependência temporal regular e sazonal. Sua notação é:

\[
ARIMA(p,d,q)(P,D,Q)_m
\]

em que os primeiros termos representam a dinâmica de curto prazo e os termos entre parênteses representam a dinâmica sazonal de período \(m\), aproximadamente anual para dados semanais.

Em linguagem simples, SARIMA tenta remover ou modelar tendência e sazonalidade e, depois, explicar como valores e erros passados ajudam a prever o futuro.

### Por que foi testado

A análise exploratória encontrou autocorrelação alta em uma semana e também em 52 e 53 semanas. Logo, seria metodologicamente incompleto não testar uma família desenhada para dependência temporal e sazonalidade.

### Como foi avaliado

Foram usadas as mesmas séries densas, os mesmos cortes temporais e os mesmos horizontes dos demais modelos. Além das métricas, foi exigida cobertura: um método que falha em muitas origens não pode ser declarado vencedor apenas nos casos em que conseguiu ajustar.

### Resultado observado

O SARIMA clássico exigiu muito tempo de execução e não alcançou cobertura estável suficiente. A dificuldade não foi tratada como detalhe de implementação: ela limita a capacidade de reproduzir e usar o modelo de forma confiável em rotina.

### Decisão final

O SARIMA clássico foi **descartado da política final por cobertura e estabilidade insuficientes**. Isso não significa que SARIMA seja inadequado em geral; significa que, nesta base, neste conjunto de especificações e nesta exigência de validação, ele não demonstrou vantagem operacional suficiente.

### Ponto de aprendizagem

Diagnóstico, convergência e cobertura fazem parte do resultado. Um método que fornece ótima previsão apenas em uma parcela das origens não responde integralmente ao problema de previsão recorrente.

---

## 4. SARIMAX com harmônicos anuais

### Ideia central

Depois da instabilidade do SARIMA clássico, foi testada uma alternativa: representar o ciclo anual por funções seno e cosseno, chamadas de harmônicos, dentro de um modelo SARIMAX. Para o tempo \(t\), um par harmônico pode ser escrito como:

\[
\sin(2\pi kt/m) \quad \text{e} \quad \cos(2\pi kt/m)
\]

Os harmônicos descrevem ondas anuais suaves. A parte ARIMA/SARIMAX modela a dependência que permanece depois de considerar essas ondas.

### Diferença para uma regressão dinâmica geral

No planejamento inicial, a ideia de ARIMAX incluía possíveis covariáveis externas, como clima ou indicadores de vigilância. Essas covariáveis **não foram incluídas** no resultado final porque seria necessário demonstrar disponibilidade sem atraso, qualidade, cobertura nacional e ausência de vazamento de informação. O SARIMAX harmônico usado aqui é diferente: os termos externos são funções determinísticas do próprio calendário, conhecidas antecipadamente.

### Por que foi testado

O objetivo foi preservar uma representação flexível da sazonalidade anual sem estimar uma estrutura SARIMA sazonal clássica excessivamente custosa ou instável.

### Resultado observado

O SARIMAX harmônico apresentou estabilidade de execução e cobertura completa, mas não superou ETS em 1 e 4 semanas nem o ingênuo sazonal em 8 e 13 semanas. Portanto, a estabilidade melhorou, mas não houve ganho preditivo suficiente para alterar a escolha final.

### Decisão final

O método permanece documentado como tentativa válida e reproduzível, mas não integra a política operacional. Ele pode ser reavaliado no futuro se houver nova janela independente, mudança no padrão sazonal ou covariáveis futuras devidamente validadas.

### Ponto de aprendizagem

Resolver a convergência de uma família não obriga sua adoção. Um modelo precisa superar alternativas mais simples no objetivo que realmente importa: prever o futuro.

---

## 5. Previsão hierárquica e reconciliação

### Ideia central

Previsão hierárquica não é um único modelo gerador. É uma forma de combinar previsões em níveis que se somam. Neste trabalho:

\[
27\ \text{UFs} \longrightarrow 5\ \text{regiões} \longrightarrow Brasil
\]

Uma previsão coerente precisa satisfazer simultaneamente:

\[
\text{Região} = \sum \text{UFs da região}
\]

\[
\text{Brasil} = \sum \text{cinco regiões}
\]

### Por que foi necessária

As melhores previsões independentes em cada nível podem não somar corretamente. Isso ocorreu na Base V2 em 1 e 4 semanas porque Brasil e regiões usam ETS, enquanto UFs usam ingênuo. Não é erro: são modelos independentes com sinais diferentes. Mas é um problema se a intenção é divulgar, na mesma reunião ou boletim, UFs, regiões e Brasil.

### Base V2: ponto de partida da reconciliação

Base V2 não é uma nova base de dados. É a coleção de previsões independentes escolhidas após a comparação não hierárquica:

- Brasil e regiões: ETS amortecido em 1 e 4 semanas; ingênuo sazonal em 8 e 13;
- UFs: ingênuo em 1 e 4 semanas; ingênuo sazonal em 8 e 13.

Em 8 e 13 semanas, todos os níveis usam a mesma regra sazonal e já são coerentes por construção. O desafio de reconciliação está concentrado em 1 e 4 semanas.

### Métodos comparados

| Método | Como funciona | Resultado neste estudo |
|---|---|---|
| Bottom-up | Soma as previsões das UFs para obter regiões e Brasil | Coerente, mas piorou previsões agregadas em curto prazo. |
| Top-down global | Parte do agregado e distribui por proporções médias | Coerente, mas não trouxe ganho uniforme. |
| Top-down sazonal | Distribui o agregado usando proporções sazonais | Ajudou UFs em horizontes longos, mas não foi melhor em curto prazo. |
| WLS estrutural | Ajusta todos os nós ponderando a estrutura hierárquica | Coerente, porém gerou valores negativos materiais. |
| MinT-OAS | Usa estrutura regularizada dos erros de previsão | Coerente, mas também gerou negativos sem restrição. |
| MinT não negativo | Impõe UFs maiores ou iguais a zero dentro da otimização | Coerente, não negativo e melhor compromisso operacional em curto prazo. |

### O que é MinT

MinT significa *minimum trace*. Ele reconcilia previsões usando uma estimativa da covariância dos erros, dando mais peso relativo a informações consideradas mais confiáveis. A covariância bruta, neste estudo, foi instável porque algumas UFs têm séries muito esparsas. Por isso, foi aplicado *shrinkage* OAS, que aproxima a matriz de covariância de uma forma mais estável sem apagar totalmente as relações observadas.

### Por que a não negatividade foi necessária

WLS estrutural e MinT-OAS, sem restrição, geraram previsões negativas. Cortar esses valores para zero depois da reconciliação quebraria as somas hierárquicas. A solução foi incluir a condição de não negatividade dentro da otimização das 27 UFs e formar regiões e Brasil pela soma dessas folhas.

As 232 otimizações previstas convergiram. A diferença máxima de agregação foi 8,64 × 10⁻¹¹, que é somente imprecisão numérica de máquina. Nenhuma previsão final ficou negativa.

### Resultado observado

Em 1 semana, o MASE das UFs caiu de 1,145 na Base V2 para 1,133 com MinT não negativo; em 4 semanas, caiu de 2,285 para 2,211. As regiões também melhoraram levemente em uma semana, de 0,545 para 0,534. O custo foi pequena piora para Brasil em uma e quatro semanas e para regiões em quatro semanas.

### Decisão final

MinT não negativo foi escolhido para 1 e 4 semanas **quando a saída precisa conter todos os níveis geográficos coerentes**. Ele não substitui automaticamente a Base V2 para um boletim nacional isolado, onde a Base V2 teve menor erro médio de curto prazo.

---

## Política anterior por horizonte (etapa 37)

| Horizonte | Método operacional | Objetivo priorizado |
|---|---|---|
| 1 semana | MinT não negativo | Coerência, contagens possíveis e melhoria das UFs. |
| 4 semanas | MinT não negativo | Mesmo compromisso para planejamento mensal aproximado. |
| 8 semanas | Base V2 sazonal | A previsão sazonal já é coerente e a reconciliação não trouxe ganho. |
| 13 semanas | Base V2 sazonal | Cenário sazonal de maior prazo, com incerteza ampla. |

Essa política é uma regra condicionada ao uso. Ela não afirma que existe um único “melhor modelo” para toda situação.

## Como os intervalos de incerteza entram na resposta

As previsões pontuais foram complementadas por faixas empíricas de 80% e 95%, formadas pelos resíduos da política final nos 58 cortes temporais. Elas respondem à pergunta “quão diferente do ponto previsto o resultado pode ser, considerando erros semelhantes no passado?”.

As faixas de 80% tiveram cobertura retrospectiva entre 76,9% e 78,4%; as de 95%, entre 89,7% e 93,1%. Portanto, devem ser chamadas de faixas empíricas de incerteza, não de garantias probabilísticas formais. Seus limites são marginais e não necessariamente se somam na hierarquia, embora os pontos previstos sejam coerentes.

## 6. Métodos especializados em intermitência — etapa 41

**Ideia.** Representar séries em que os valores positivos são separados por zeros. Muitos zeros justificam testar esses métodos, mas não garantem que sejam vencedores; o VSR também tem sazonalidade.

**Candidatos.** CrostonClassic separa tamanho positivo e intervalo entre ocorrências. CrostonSBA aplica uma correção de viés; CrostonOptimized estima a suavização. TSB atualiza probabilidade de ocorrência e tamanho positivo. ADIDA agrega períodos antes de prever e desagregar; IMAPA combina diferentes escalas de agregação. TSB_SAZONAL foi a adaptação com dessazonalização pelo perfil anual.

**Exemplo ilustrativo.** Na sequência 0, 0, 3, 0, 0, 2, um método pode estimar quantidade positiva típica e frequência de ocorrência. Não identifica obrigatoriamente a semana exata do próximo caso.

**Resultado.** Esses candidatos foram efetivamente testados no notebook 04. Não compõem as bases finais selecionadas; LightGBM apresentou menor MASE médio das UFs por horizonte. Não se deve generalizar que Croston ou TSB nunca funcionam.

## 7. GLM binomial negativo com Fourier — etapa 41

**Ideia.** Regressão para contagens com variabilidade que pode superar a média. Os termos de Fourier representam o calendário anual e o nível recente traz informação da evolução da série.

**Exemplo ilustrativo.** Duas semanas com nível recente semelhante podem receber previsões diferentes conforme a posição no ciclo sazonal.

**Uso no estudo.** Foi testado como GLM_NB_FOURIER, com previsão direta por horizonte. É uma alternativa de contagem, distinta dos métodos Croston e das árvores de boosting.

**Resultado e limite.** Não foi selecionado para a política final. O uso de uma distribuição de contagens não garante menor erro nem estabelece uma explicação causal dos casos.

## 8. LightGBM compartilhado — etapas 41 e 42

**Ideia.** Árvores de decisão combinadas por boosting aprendem relações entre atributos históricos e o alvo futuro. “Global” significa aprender com várias séries conjuntamente.

**Duas versões.** LGBM_TWEEDIE (também chamado LGBM_TWEEDIE_UF na composição) usa as 27 UFs. LGBM_GLOBAL usa os 33 nós e normaliza os valores pela média de treino de cada nó, com piso. Ambas usam perda Tweedie; não são redes neurais.

**Atributos.** Último valor conhecido e três defasagens anteriores, referência de 52 semanas relativa ao alvo, médias retrospectivas de 4/8 semanas, fração de zeros em 8 semanas e calendário do alvo. Entram também identidade da UF ou nó e, no global, nível geográfico. Não foram usados clima, mobilidade ou dados externos adicionais.

**Treinamento.** Um modelo por horizonte é reajustado a cada origem. Entram no treino somente exemplos cujo alvo já ocorreu até a origem. Os 33 nós compartilham informação, mas não equivalem a 33 séries independentes: os agregados contêm as próprias UFs.

**Resultado.** A versão UF venceu por MASE médio estadual na etapa 41, quase empatando com o sazonal em h=13. A versão global ganhou em algumas combinações de nível/horizonte na etapa 42. Os resultados após reconciliação determinaram o compromisso final.

**Limite.** Os hiperparâmetros são fixos; as escolhas reutilizam a validação. Não há garantia de ganho em dados futuros.

## Política vigente — etapa 43

| Horizonte | Base escolhida | Brasil | Regiões | UFs | Reconciliação |
|---|---|---|---|---|---|
| 1 e 4 semanas | V3 | ETS amortecido | ETS amortecido | LightGBM treinado conjuntamente nas 27 UFs | MinT-OAS não negativo |
| 8 semanas | V4 | Ingênuo sazonal | LightGBM global de 33 nós | LightGBM global de 33 nós | MinT-OAS não negativo |
| 13 semanas | V4 | Ingênuo sazonal | Ingênuo sazonal | LightGBM global de 33 nós | MinT-OAS não negativo |

Base é a tabela de previsões independentes; política é a regra de composição e reconciliação. V1–V4 são versões dessa tabela, não versões dos microdados.

A V4 independente escolheu LightGBM global para Brasil em h=4 e regiões em h=1/4, mas a política final utiliza V3 nesses horizontes. Escolher bons modelos isolados não garante o melhor conjunto após MinT.

A seleção dos modelos e da política reutiliza as mesmas 58 origens usadas para calcular as métricas. Os ganhos podem estar otimistas; a magnitude desse viés não foi estimada. Não há teste final intocado nem demonstração de significância estatística. A calibração do MinT atravessa 2020–2021. A validação usa uma versão consolidada dos registros: separar datas de treino e alvo evita o uso direto de alvos futuros no ajuste, mas não reconstitui exatamente o que estava publicado em cada origem histórica. A maturidade de 13 semanas reduz o problema das semanas recentes; não substitui snapshots históricos ou uma avaliação em tempo real.

Deep learning e covariáveis externas não foram utilizados. A ausência de covariáveis externas não impediu os ganhos do LightGBM com atributos derivados do próprio histórico.

## Glossário atualizado

- **Autocorrelação:** relação entre uma observação da série e seus próprios valores passados.
- **Base V2:** conjunto de melhores previsões independentes por nível e horizonte; não é uma nova base de microdados.
- **Baseline ou linha de base:** previsão simples que todo método mais complexo precisa superar.
- **Cobertura:** proporção de cortes em que o modelo conseguiu gerar previsão válida.
- **Coerência hierárquica:** propriedade de as previsões de UFs, regiões e Brasil respeitarem suas somas.
- **Convergência:** situação em que o algoritmo de ajuste encontrou uma solução numérica estável segundo seus critérios.
- **Covariância dos erros:** medida de como erros de previsão de diferentes nós tendem a variar juntos.
- **ETS:** família de suavização exponencial com componentes de erro, nível, tendência e sazonalidade.
- **Faixa empírica:** intervalo obtido a partir da distribuição dos erros históricos, sem garantia probabilística perfeita.
- **Horizonte:** número de semanas à frente que se deseja prever.
- **Ingênuo:** método que repete o último valor observado.
- **Ingênuo sazonal:** método que repete a referência da temporada anterior.
- **MAE:** média dos erros absolutos, em número de casos.
- **MASE:** MAE escalonado por uma referência simples; permite comparar séries de tamanhos distintos.
- **MinT:** método de reconciliação que busca minimizar uma medida ponderada dos erros dentro da hierarquia.
- **Não negatividade:** restrição de que contagens previstas sejam iguais ou maiores que zero.
- **Origem de previsão:** última semana conhecida quando uma previsão é emitida.
- **Previsão fora da amostra:** previsão de um período que não foi usado para ajustar o modelo.
- **Reconciliação:** ajuste de previsões para torná-las coerentes entre níveis geográficos.
- **RMSE:** raiz do erro quadrático médio; penaliza mais fortemente erros grandes.
- **SARIMA:** modelo ARIMA com componentes sazonais.
- **SARIMAX harmônico:** SARIMAX que representa sazonalidade por senos e cossenos do calendário.
- **Sazonalidade:** padrão que tende a se repetir em certos períodos do calendário.
- **Shrinkage OAS:** regularização que torna a estimativa de covariância mais estável.
- **Série intermitente:** série com muitos períodos de contagem zero.
- **Tendência amortecida:** tendência cuja projeção é reduzida gradualmente, evitando extrapolação indefinida.
- **Validação temporal expansiva:** avaliação em que o treino cresce ao longo do tempo e nenhum dado futuro entra no ajuste.
- **Vazamento temporal:** uso de informações futuras durante o treino ou a avaliação.

## Leituras e fontes metodológicas

- Hyndman, R. J. e Athanasopoulos, G. [Forecasting: Principles and Practice](https://otexts.com/fpp3/).
- Hyndman, R. J. et al. [Optimal combination forecasts for hierarchical time series](https://collaborate.robjhyndman.com/publications/hierarchical/), 2011.
- Wickramasuriya, S. L., Athanasopoulos, G. e Hyndman, R. J. [Optimal forecast reconciliation for hierarchical and grouped time series through trace minimization](https://robjhyndman.com/papers/MinT.pdf), 2019.

## Relação com os resultados do projeto

Os scripts, tabelas e gráficos que sustentam este guia estão documentados em `MODELAGEM_AVALIACAO_3_ETAPA/EXPLICACAO_DAS_DECISOES_MODELAGEM_AVALIACAO_V2.md` e nos resultados versionados em `*/resultados_scripts/`.
