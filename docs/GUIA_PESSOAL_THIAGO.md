# Guia pessoal do Thiago — entender e apresentar o trabalho

Preparação para segunda-feira, 16 de novembro de 2026.
Versão conferida em 14/11/2026 contra os notebooks 04–06, o código compartilhado e os quadros da etapa 43.
Este é um material de estudo dirigido a você. Não precisa ser lido em voz alta nem entregue como artigo.

## 1. O trabalho em uma fala de abertura

“Nosso trabalho usa registros públicos de SRAG para prever contagens semanais de crianças menores de dois anos hospitalizadas com confirmação de VSR. Primeiro tratamos os dados e estudamos sazonalidade e diferenças regionais. Depois comparamos modelos clássicos e ampliamos o estudo para métodos de intermitência e LightGBM. Por fim, reconciliamos as previsões para que UFs, regiões e Brasil sejam compatíveis. A extensão melhorou o erro médio em quase todas as combinações avaliadas, mas ainda precisamos de uma avaliação futura independente.”

Você não precisa abrir a fala com V1, V2, V3 e V4. Esses nomes explicam o desenvolvimento e podem entrar quando o professor perguntar sobre a evolução.

## 2. O que exatamente estamos contando

São notificações com hospitalização e confirmação específica de VSR, em crianças de zero a menos de 24 meses. Quem já completou dois anos não entra no critério.

A série usa a semana de início dos sintomas e a UF de residência. Portanto, diga “casos hospitalizados organizados por semana de sintomas”. Não prometa prever diretamente admissões hospitalares daquela semana ou leitos ocupados naquela UF.

Usamos SIVEP-Gripe. SINASC foi cogitado na proposta, mas não entrou nos modelos finais. Não usamos clima, mobilidade ou outras variáveis externas.

A fonte tinha 4.678.812 notificações; o recorte e a deduplicação deixaram 158.358. A série madura usada na modelagem tem 395 semanas. São 33 séries: 27 UFs, cinco regiões e Brasil. Somar os três níveis contaria as mesmas pessoas várias vezes.

## 3. Por que limpamos os dados antes de prever

Precisávamos garantir que todos os modelos recebessem a mesma definição de caso, de tempo e de território. Uma notificação repetida poderia contar duas vezes; datas ruins poderiam colocar casos no ano errado; ausência de exame não poderia virar resultado negativo.

Investigamos duas notificações duplicadas e selecionamos uma versão por regra temporal auditável. Em seguida agregamos por semana e verificamos as somas.

“Madura” significa semana fechada e suficientemente distante do corte da fonte para reduzir incompletude. O P95 anual máximo de atraso foi 86 dias; adotamos 13 semanas. A última madura é 19/07/2026. Essa regra não garante que conhecíamos os valores finais em todas as origens históricas: os arquivos são uma versão consolidada.

## 4. O que a exploração nos ensinou

Havia repetição anual, mas os picos e volumes mudavam entre regiões e anos. Muitas UFs tinham poucos registros: 13 passaram de 50% das semanas com zero. Brasil e regiões eram mais densos.

Isso deu duas hipóteses: testar modelos com sazonalidade nos agregados e métodos capazes de lidar com esparsidade nas UFs. Zeros registrados não significam certeza de ausência do vírus.

A pandemia mudou o contexto. Mantivemos 2020 e 2021 e reconhecemos que circulação, testagem e notificação podem ter mudado. Não demonstramos “confusão de COVID com VSR” nem atribuímos toda a variação a uma causa.

## 5. Três palavras que você precisa separar

**Dados:** as contagens observadas, que são a entrada do estudo.

**Modelo-base:** a regra que recebe o histórico e calcula uma previsão. Exemplos: ingênuo, ETS, LightGBM.

**Base de previsões:** uma tabela com essas previsões de cada lugar, origem e horizonte. Ela pode misturar modelos.

**Reconciliação:** um procedimento aplicado às previsões para que as somas geográficas sejam respeitadas. MinT é esse procedimento.

**Política:** a regra completa que determina quais previsões-base usar e qual reconciliação aplicar para cada horizonte.

Exemplo hipotético: ETS prevê 100 para o país e os modelos estaduais somam 120. MinT combina as informações segundo a estrutura dos erros; a solução final pode ser outro total, distribuído de modo coerente. Ele não obriga o Brasil a permanecer em 100 nem apenas faz uma média simples.

## 6. V1, V2, V3 e V4 — a história sem mistério

| Nome | O que mudou | O que não significa |
|---|---|---|
| Base V1, etapa 28 | UFs usavam sazonal em todos os horizontes; agregados seguiam as escolhas clássicas | Não é versão 1 do SIVEP |
| Base V2, etapa 30 | UFs passam a ingênuo em 1/4; mantêm sazonal em 8/13 | Não é a saída já reconciliada |
| Base V3, etapa 41 | LightGBM das 27 UFs substitui a camada estadual da V2 | Não significa LightGBM em todos os níveis |
| Base V4, etapa 42 | Compara V2, LightGBM UF e LightGBM de 33 nós por nível/horizonte | Não substitui integralmente V3 na decisão final |

A **política V2 anterior**, da etapa 37, pega a Base V2 e aplica MinT em 1/4; em 8/13 mantém a previsão sazonal já coerente.

A **política final**, da etapa 43, pega V3 em 1/4 e V4 em 8/13 e aplica MinT não negativo a todos.

Quando disser “melhorou em relação à V2”, explique se está comparando com a base independente ou com a política anterior. Os números principais do README comparam políticas.

## 7. Quais modelos clássicos testamos

O ingênuo repete o último valor. O sazonal repete a observação de 52 semanas antes da semana-alvo; essa é uma aproximação semanal do ano, não um alinhamento perfeito de semanas epidemiológicas 52/53.

ETS aprende nível, tendência e sazonalidade. A tendência amortecida evita projetar indefinidamente o mesmo crescimento ou queda. Foi selecionado nos agregados em 1/4 semanas.

SARIMA tentou representar dependência regular e anual, mas teve dificuldades de estabilidade/cobertura. SARIMAX com harmônicos usou ondas anuais seno/cosseno e foi estável, sem ganhar das escolhas clássicas. Diga que as especificações testadas não venceram, não que toda a família SARIMA seja ruim.

## 8. Quais métodos foram acrescentados para intermitência

| Método | Intuição |
|---|---|
| CrostonClassic | Estima separadamente tamanho positivo e intervalo entre ocorrências |
| CrostonSBA | Aplica correção de viés à abordagem Croston |
| CrostonOptimized | Ajusta parâmetros de suavização |
| TSB | Atualiza probabilidade de ocorrência e tamanho positivo |
| ADIDA | Agrega semanas, prevê e desagrega |
| IMAPA | Combina diferentes níveis de agregação temporal |
| TSB_SAZONAL | Adapta TSB para considerar o perfil sazonal |
| GLM_NB_FOURIER | Regressão de contagens com binomial negativa, calendário e nível recente |

GLM é um modelo de contagens, não uma variante de Croston. Esses métodos foram candidatos; não foram escolhidos para compor a política final. O vencedor por MASE médio estadual foi LightGBM, com empate praticamente técnico em h=13 contra o sazonal.

## 9. O aprendizado de máquina que de fato usamos

LightGBM combina árvores de decisão. Uma árvore divide exemplos por condições; várias árvores corrigem sucessivamente os erros da combinação. Não é deep learning.

Treinamos duas versões: uma aprende conjuntamente com 27 UFs; a outra com os 33 nós. São modelos globais no sentido de compartilharem aprendizado entre séries. O nome LGBM_GLOBAL foi reservado no código à segunda.

Ambas usam perda Tweedie. Os atributos vêm do passado: valores recentes, médias retrospectivas, referência sazonal, zeros e calendário, com identificação da série. Não foi necessário adicionar clima para obter ganho.

A versão de 33 nós normaliza o volume pela média de treino de cada série e depois devolve a previsão à escala de casos. Não são 33 amostras independentes: Brasil e regiões somam as UFs.

Há um modelo direto por horizonte. Para prever h=4, o treino contém exemplos históricos cujo resultado quatro semanas depois já era conhecido até a origem. Isso evita usar o alvo futuro no ajuste.

## 10. Por que reconciliar depois do LightGBM

Aprender com várias séries não obriga automaticamente suas previsões a somarem. Mesmo o LightGBM global precisa de reconciliação.

Bottom-up soma folhas. Top-down distribui o agregado. WLS estrutural pondera segundo a estrutura. MinT usa os erros históricos e suas relações para ponderar a combinação.

OAS estabiliza a matriz de covariância dos erros. “Não negativo” significa que as UFs são restringidas a valores maiores ou iguais a zero dentro da solução; regiões e Brasil são somados dessas folhas. Não é simplesmente cortar cada número negativo no final.

## 11. A tabela que você deve saber explicar

| Horizonte | Base escolhida | Brasil | Regiões | UFs | Reconciliação |
|---|---|---|---|---|---|
| 1 e 4 semanas | V3 | ETS amortecido | ETS amortecido | LightGBM treinado conjuntamente nas 27 UFs | MinT-OAS não negativo |
| 8 semanas | V4 | Ingênuo sazonal | LightGBM global de 33 nós | LightGBM global de 33 nós | MinT-OAS não negativo |
| 13 semanas | V4 | Ingênuo sazonal | Ingênuo sazonal | LightGBM global de 33 nós | MinT-OAS não negativo |

Leia assim: em quatro semanas, ETS faz Brasil/regiões, LightGBM UF faz estados, e MinT reconcilia tudo.

Em oito, Brasil vem da referência sazonal e regiões/UFs do LightGBM global; as somas podem divergir, por isso agora também aplicamos MinT.

Em 13, Brasil e regiões usam sazonal, UFs usam LightGBM global, e depois reconciliamos.

## 12. Por que a política não usa V4 em tudo

Escolher o menor erro de cada nível antes do MinT não garante o menor erro depois dele. A comparação final é de conjuntos.

Em h=1, V4 reconciliada é melhor no Brasil: MASE 0,274 contra 0,288 da V3. V3 é melhor em regiões e UFs. Em h=4, V3 é melhor nos agregados, V4 nas UFs: 1,889 contra 1,918. A escolha é um compromisso entre níveis; não há uma alternativa que ganhe em tudo.

Se o professor perguntar qual peso demos a cada nível, diga que a política foi escolhida pela leitura dos resultados por nível/horizonte, sem uma função única de utilidade operacional formalmente fixada. Formalizar esses pesos seria uma melhoria metodológica.

## 13. Os resultados para guardar

| Nível | h=1: anterior → atual | h=4: anterior → atual | h=8: anterior → atual | h=13: anterior → atual |
|---|---|---|---|---|
| Brasil | 0,333 → 0,288 | 1,202 → 0,802 | 1,575 → 1,541 | 1,522 → 1,457 |
| Regiões | 0,535 → 0,480 | 1,417 → 1,113 | 1,775 → 1,700 | 1,883 → 1,889 |
| UFs | 1,133 → 1,077 | 2,211 → 1,918 | 2,990 → 2,745 | 3,122 → 3,056 |

MASE menor é melhor. Não é percentual de acerto. Sua escala foi calculada com erro sazonal no treino de cada origem; ficar abaixo de um não equivale automaticamente a vencer o sazonal fora da amostra no mesmo horizonte.

MAE é erro absoluto médio em casos. Para Brasil h=4, caiu de aproximadamente 190,5 para 121,9. RMSE dá mais peso a erros grandes.

São 11 de 12 combinações com MASE menor frente à política anterior. Regiões em h=13 pioraram um pouco. A média das UFs não prova que todas as 27 melhoraram.

## 14. A previsão demonstrativa não é para a próxima segunda-feira

Ela parte de 19/07/2026. Os alvos são 26/07, 16/08, 13/09 e 18/10. Brasil recebe aproximadamente 683, 329, 190 e 88 casos nessas semanas.

h=4 significa a contagem na quarta semana à frente, não a soma das próximas quatro. Valores decimais são estimativas de contagem esperada, não crianças fracionadas.

Não diga que estamos prevendo novembro. Para isso precisaríamos atualizar as entradas e enfrentar a defasagem entre as últimas semanas maduras e o presente.

## 15. Incerteza, alertas e o que não prometer

A faixa de 80% do Brasil h=4 vai de aproximadamente 177 a 677. Ela mostra que o ponto 329 está longe de ser certeza.

As faixas foram construídas com erros retrospectivos e têm cobertura abaixo da nominal. Seus limites não somam na hierarquia; só os pontos são reconciliados. O LOO remove o próprio erro, mas não respeita uma avaliação estritamente para a frente dos intervalos.

A etapa 43 não apontou ajuste acima do P95 histórico. Isso significa apenas que o tamanho da correção MinT ficou dentro desse critério. Não comprova acerto ou segurança clínica.

## 16. As limitações que você deve assumir com tranquilidade

A seleção dos modelos e da política reutiliza as mesmas 58 origens usadas para calcular as métricas. Os ganhos podem estar otimistas; a magnitude desse viés não foi estimada. Não há teste final intocado nem demonstração de significância estatística. A calibração do MinT atravessa 2020–2021. A validação usa uma versão consolidada dos registros: separar datas de treino e alvo evita o uso direto de alvos futuros no ajuste, mas não reconstitui exatamente o que estava publicado em cada origem histórica. A maturidade de 13 semanas reduz o problema das semanas recentes; não substitui snapshots históricos ou uma avaliação em tempo real.

Diferenças pequenas não foram submetidas a uma demonstração de significância. Também não provamos que a diversidade dos modelos causou o ganho; é uma interpretação compatível com a comparação.

O trabalho tem valor por organizar uma pergunta, comparar alternativas e documentar decisões. Não depende de fingir previsão perfeita ou ausência de limitações.

## 17. Perguntas que podem aparecer

**“Por que vocês não ficaram só com ETS?”** Porque UFs têm comportamento diferente e o LightGBM compartilhado melhorou as métricas; ETS permaneceu onde sua combinação foi útil.

**“Os modelos intermitentes ganharam?”** Não na regra de seleção por MASE médio estadual. Testamos a hipótese; quem entrou na base foi LightGBM.

**“Por que não trocar tudo por machine learning?”** Porque o conjunto com ETS nos agregados e LightGBM nas UFs foi competitivo após MinT. As escolhas variam por horizonte e nível.

**“Vocês estão usando dados futuros?”** O ajuste de cada origem restringe atributos e alvos de treino ao passado. Porém a fonte é consolidada, não snapshots históricos, e a política foi selecionada nas mesmas origens avaliadas. Essas limitações estão declaradas.

**“Isso vai dizer quantos leitos abrir?”** Não diretamente. O desfecho é por residência e início de sintomas; seriam necessárias informações assistenciais adicionais para converter em ocupação.

**“O ganho é estatisticamente comprovado?”** Temos redução observada das métricas, sem teste externo intocado nem demonstração formal de significância.

## 18. Como navegar sem se perder

Leia [ORDEM_DE_LEITURA.md](ORDEM_DE_LEITURA.md). Os arquivos 01–06 contêm etapas 1–43. Código comum fica em src/vsr; docs guarda as explicações. Resultados finais atuais estão na pasta etapa_43_politica_final.

Você pode estudar as saídas salvas sem executar o pipeline. Não precisa refazer o SARIMA para entender a história.

Antes de apresentar, consiga explicar com suas palavras: o que contamos; por que semanas maduras; como avaliamos; diferença entre modelo/base/política; o que mudou com LightGBM; e uma limitação importante.
