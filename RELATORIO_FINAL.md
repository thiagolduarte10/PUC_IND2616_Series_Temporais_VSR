# Relatório final — Previsão hierárquica de internações por VSR no Brasil

**Disciplina:** IND2616 — Séries Temporais  
**Programa:** Mestrado, PUC-Rio  
**Professor:** Fernando Cyrino  
**Grupo:** Thiago Paes, Joan Souza, Matheus Accioly e Isabelle Gagno  
**Reprodução local concluída em:** 08/11/2026

## Resumo

Este trabalho construiu e avaliou previsões semanais de internações por Síndrome Respiratória Aguda Grave (SRAG) associada ao vírus sincicial respiratório (VSR) em crianças menores de dois anos. O recorte é observado em três níveis geográficos que formam uma hierarquia: 27 Unidades da Federação (UFs), cinco regiões e Brasil. A contribuição principal não é apenas comparar modelos isolados: é produzir uma política de previsão que preserve a coerência entre os níveis geográficos, isto é, que o Brasil corresponda à soma das regiões e cada região à soma de suas UFs, sem gerar contagens negativas.

Foram usados microdados oficiais do SIVEP-Gripe, publicados pelo OpenDataSUS, de 2019 a 2026. Após congelamento da fonte, validação, recorte epidemiológico, verificação laboratorial, deduplicação e tratamento dos atrasos de disponibilidade, foram obtidas 158.358 notificações elegíveis. Elas foram agregadas em um painel semanal com 407 semanas; somente 395 semanas maduras entraram no treinamento e na avaliação, para reduzir viés causado por notificações tardias.

Brasil e regiões apresentam sazonalidade anual e forte dependência temporal. As UFs, porém, são heterogêneas e muitas são intermitentes: 13 têm mais de metade das semanas maduras sem casos. Por isso, não foi razoável impor o mesmo modelo a toda a hierarquia. A avaliação temporal, com 58 origens expansivas e horizontes de 1, 4, 8 e 13 semanas, mostrou que a melhor referência depende do horizonte. A política final usa MinT não negativo em 1 e 4 semanas, quando é necessário comunicar uma previsão coerente para todos os níveis, e preserva a Base V2 sazonal em 8 e 13 semanas.

O estudo não estima toda a circulação comunitária de VSR nem substitui a vigilância epidemiológica. Ele estima a série de notificações hospitalares confirmadas pelo recorte definido. A previsão operacional deve ser lida como apoio à preparação de demanda, acompanhada de faixas de incerteza e de alertas de plausibilidade.

## 1. Problema e pergunta de pesquisa

O VSR é uma causa relevante de doença respiratória em crianças pequenas e pode gerar pressão sazonal sobre serviços pediátricos. Essa pressão não ocorre simultaneamente, nem com a mesma intensidade, em todas as regiões brasileiras. Assim, uma previsão nacional isolada pode esconder necessidades locais; por outro lado, previsões estaduais independentes podem somar valores incompatíveis com o total regional ou nacional.

A pergunta orientadora foi:

> É possível prever, com antecedência de uma a 13 semanas, o número semanal de internações por SRAG associada ao VSR em crianças menores de dois anos, preservando a coerência entre UF, região e Brasil?

O objetivo prático é oferecer uma leitura antecipada de demanda potencial, útil para discussão de preparação de leitos pediátricos, equipes, testes e fluxos assistenciais. Não se trata de uma ferramenta de decisão clínica individual nem de uma estimativa da incidência total de VSR na população.

## 2. Dados e definição do desfecho

### Fonte e versão usada

A fonte primária foi o [SIVEP-Gripe / OpenDataSUS — SRAG 2019–2026](https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026). Foram congelados oito arquivos Parquet anuais oficiais, de 2019 a 2026, depois de verificar URL, tamanho e hash SHA-256. Os arquivos somam 333,67 MB e contêm 4.678.812 notificações brutas, com 194 campos presentes em todos os anos.

O congelamento é parte do método: os arquivos públicos podem ser republicados e o portal pode mudar. A análise documenta a versão realmente consultada em vez de afirmar que ela continuará sendo a versão mais recente no futuro.

### Recorte epidemiológico

Cada registro da base final atende simultaneamente aos seguintes critérios:

- data de início de sintomas (`DT_SIN_PRI`) válida;
- idade convertida para meses entre 0 e menor que 24;
- UF de residência válida entre as 27 UFs (`SG_UF`);
- hospitalização indicada (`HOSPITAL = 1`);
- confirmação específica de VSR por PCR (`PCR_VSR = 1`) ou antígeno (`AN_VSR = 1`);
- uma única versão por notificação, após deduplicação auditável.

O desfecho é, portanto, uma **contagem semanal de internações notificadas e confirmadas por VSR**, não uma medida de todas as infecções por VSR, de toda a demanda ambulatorial ou da gravidade clínica individual. A cobertura de exames específicos varia entre anos; ausência de exame não foi interpretada como resultado negativo.

## 3. Tratamento e qualidade dos dados

O tratamento foi organizado como uma cadeia reproduzível, antes de qualquer ajuste de modelo.

| Etapa | Decisão | Motivo e resultado |
|---|---|---|
| Fonte | Congelar oito arquivos oficiais | Permite reproduzir exatamente a base analisada. |
| Estrutura | Inventariar as 194 colunas em todos os anos | Evita escolher campos apenas por semelhança de siglas. |
| Tempo | Usar início de sintomas como relógio da série | A data é completa e epidemiologicamente mais próxima do início do evento. |
| Geografia | Usar UF de residência | Tem completude alta e corresponde ao local de residência do caso. |
| Confirmação | Unir PCR e antígeno para VSR | Evita perder confirmações exclusivas por antígeno e evita dupla contagem. |
| Duplicidades | Escolher uma versão por notificação com regra temporal explícita | Foram investigadas duas notificações duplicadas; duas linhas foram removidas. |
| Atrasos | Marcar maturidade, sem apagar semanas recentes | Permite separar dado observado de dado suficientemente consolidado. |

A base individual final contém **158.358** notificações elegíveis. Os registros foram agregados pela semana de início de sintomas. O painel semanal possui 13.431 linhas, correspondentes a 33 nós geográficos por 407 semanas, de 30/12/2018 a 11/10/2026. Nas semanas fechadas, a soma das UFs coincide exatamente com Brasil.

### Maturidade da informação

O estudo mediu a defasagem entre o evento e sua disponibilidade no sistema. A mediana anual de atraso ficou entre 8 e 13 dias; o maior percentil 95 anual foi 86 dias, em 2021. Como critério conservador, uma semana foi classificada como madura quando estava fechada e havia transcorrido pelo menos 13 semanas desde o corte da fonte, 19/10/2026.

Assim, as 395 semanas até 19/07/2026 foram usadas em treino e avaliação. As 12 semanas posteriores não foram tratadas como zero nem usadas como alvo final; elas podem receber notificações e resultados laboratoriais posteriormente. Essa decisão evita que um modelo seja punido ou favorecido por uma comparação com semanas ainda incompletas.

## 4. O que a análise exploratória encontrou

Brasil e regiões apresentaram picos anuais claros. No Brasil, os picos observados nas temporadas completas ocorreram entre as semanas epidemiológicas 11 e 19, aproximadamente entre março e maio. O Sudeste e o Centro-Oeste exibiram comportamento mais precoce e concentrado; o Nordeste apresentou picos mais tardios nos anos recentes; Norte e Sul mostraram maior variação de timing.

A sazonalidade não implica repetição perfeita. A autocorrelação de uma semana foi 0,987 para Brasil e variou de 0,965 a 0,983 nas regiões. Nas defasagens anuais de 52 e 53 semanas, a autocorrelação brasileira permaneceu alta, 0,845 e 0,874. Há dependência de curto prazo e sinal anual, mas também mudanças de nível e de amplitude entre temporadas.

Os anos de 2020 e 2021 foram atípicos e não foram excluídos. A análise os preserva como parte do histórico, reconhecendo que medidas sanitárias, oferta de testes, comportamento de procura e rotinas de notificação podem ter afetado os registros. Esse estudo descreve os dados observados; não atribui causalmente essas mudanças à pandemia ou a uma única política.

Também há grande heterogeneidade espacial. O Sudeste concentra 42,9% dos casos maduros, enquanto o Norte concentra 5,5%. Treze UFs têm mais de 50% de semanas maduras com zero caso; Piauí, Mato Grosso, Tocantins e Alagoas superam 70%. Em contraste, São Paulo tem 3,0% de semanas zero. Essa intermitência explica por que previsões estaduais precisam ser tratadas de modo diferente das séries densas de Brasil e regiões.

## 5. Desenho da avaliação

Em vez de separar semanas aleatoriamente, foi criada validação temporal expansiva. Cada previsão usa somente informação disponível em sua data de origem; com o tempo, o conjunto de treino cresce. Foram usados 58 cortes por série, iniciando com pelo menos 156 semanas de histórico e avançando a cada quatro semanas, com a última origem em 19/04/2026.

Foram avaliados quatro horizontes:

- **1 semana:** acompanhamento imediato;
- **4 semanas:** planejamento aproximadamente mensal;
- **8 semanas:** planejamento de cerca de dois meses;
- **13 semanas:** cenário de aproximadamente um trimestre.

Para Brasil e cinco regiões, cada modelo foi avaliado em 6 séries × 58 cortes × 4 horizontes, totalizando 1.392 previsões. Para a hierarquia completa, cada estratégia foi avaliada em 33 nós × 58 cortes × 4 horizontes, totalizando 7.656 previsões.

As métricas foram MAE, RMSE e MASE. MAE e RMSE mantêm a unidade de casos; MASE permite comparar escalas muito diferentes. A comparação também exigiu cobertura completa, ausência de valores impossíveis e coerência geográfica quando aplicável.

## 6. Modelos e referências comparados

As referências simples foram parte essencial do experimento. Um modelo complexo só é útil se superar regras plausíveis de persistência e sazonalidade.

| Família | Papel no estudo | Resultado principal |
|---|---|---|
| Ingênuo | Repete a última observação | Forte para curtíssimo prazo em UFs intermitentes. |
| Ingênuo sazonal | Reutiliza valor da temporada anterior | Difícil de superar em 8 e 13 semanas. |
| ETS amortecido | Representa nível, tendência amortecida e sazonalidade | Melhor referência para Brasil e regiões em 1 e 4 semanas. |
| SARIMA clássico | Avalia dinâmica ARIMA sazonal | Não atingiu cobertura suficiente; foi descartado transparentemente. |
| SARIMAX harmônico | Representa ciclo anual por harmônicos | Estável, mas não superou as referências selecionadas. |

O ajuste ETS inicial apresentou dificuldades de convergência. A solução foi uma inicialização heurística robusta, sem mudar a definição da tarefa. Após essa medida, 348 de 348 ajustes esperados convergiram. O SARIMA clássico, em contraste, apresentou cobertura insuficiente e não foi promovido somente por ser mais sofisticado.

Para Brasil e regiões, o ETS amortecido obteve MASE médio de 0,507 em uma semana e 1,311 em quatro semanas. Em oito e 13 semanas, a referência ingênua sazonal foi mais robusta, com MASE de 1,741 e 1,823. A escolha não hierárquica passou a ser, portanto, dependente do horizonte.

## 7. Hierarquia geográfica e reconciliação

A estrutura geográfica possui 27 folhas (UFs), cinco agregados regionais e Brasil. Previsões feitas separadamente podem ser boas em seu próprio nível, mas incoerentes quando somadas. A Base V2 foi construída para representar a melhor previsão independente por tipo de série e horizonte:

- Brasil e regiões: ETS amortecido em 1 e 4 semanas; ingênuo sazonal em 8 e 13;
- UFs: ingênuo em 1 e 4 semanas; ingênuo sazonal em 8 e 13.

Essa Base V2 é uma coleção de previsões independentes, não uma nova base de dados. Ela reduz muito a incoerência de curto prazo em relação à primeira base, mas não a elimina por construção. Foram então comparados bottom-up, top-down global, top-down sazonal, WLS estrutural, MinT com shrinkage OAS e MinT não negativo.

Bottom-up, top-down e WLS obtiveram coerência, porém não apresentaram ganho uniforme. WLS estrutural e MinT-OAS sem restrição produziram previsões negativas materiais; para contagem de internações, esse resultado não é operacionalmente aceitável. Simplesmente truncar valores negativos em zero quebraria a coerência recém-construída.

O MinT não negativo resolveu o problema impondo não negatividade nas 27 UFs dentro da otimização e recalculando regiões e Brasil pela agregação. Não é uma correção posterior. Todas as 232 otimizações convergiram; a diferença máxima de agregação foi 8,64 × 10⁻¹¹, compatível com precisão numérica.

## 8. Resultado da comparação hierárquica

Não houve vencedor absoluto. A tabela abaixo resume o MASE médio da Base V2 e da política hierárquica escolhida nos horizontes em que a reconciliação é aplicada.

| Nível | Horizonte | Base V2 | Política hierárquica | Leitura |
|---|---:|---:|---:|---|
| Brasil | 1 semana | 0,315 | 0,332 | Base V2 é melhor para Brasil isolado. |
| Brasil | 4 semanas | 1,110 | 1,202 | Base V2 é melhor para Brasil isolado. |
| Região | 1 semana | 0,545 | 0,534 | Política melhora levemente. |
| Região | 4 semanas | 1,351 | 1,417 | Base V2 é melhor. |
| UF | 1 semana | 1,145 | 1,133 | Política melhora UFs. |
| UF | 4 semanas | 2,285 | 2,211 | Política melhora UFs. |

Em oito e 13 semanas, a Base V2 e a política final coincidem: a previsão ingênua sazonal já é coerente por construção e a reconciliação não trouxe ganho adicional demonstrado.

A política final é:

| Horizonte | Previsão recomendada | Razão |
|---|---|---|
| 1 semana | MinT não negativo | Coerente, não negativa e melhor para UFs. |
| 4 semanas | MinT não negativo | Mesmo compromisso: melhora nas UFs e coerência total. |
| 8 semanas | Base V2 sazonal | Já coerente e estável; sem benefício da reconciliação. |
| 13 semanas | Base V2 sazonal | Mesmo argumento de 8 semanas. |

Para um boletim nacional isolado de curto prazo, a Base V2 direta pode ser preferível. Para divulgar simultaneamente UF, região e Brasil, a política hierárquica é a escolha mais defensável porque entrega uma única visão territorial consistente e sem contagens impossíveis.

## 9. Previsão operacional e incerteza

Após encerrar a validação, a política foi aplicada à última origem madura, 19/07/2026, para produzir previsões de 26/07/2026 a 18/10/2026. Foram geradas 132 previsões: 33 nós por quatro horizontes.

| Horizonte | Brasil: previsão final | Faixa empírica de 80% | Faixa empírica de 95% |
|---|---:|---:|---:|
| 1 semana | 751 | 668–829 | 606–892 |
| 4 semanas | 556 | 268–914 | 0–1.097 |
| 8 semanas | 187 | 0–693 | 0–1.267 |
| 13 semanas | 83 | 0–569 | 0–1.126 |

As faixas foram obtidas a partir de resíduos históricos da política final e avaliadas por cobertura leave-one-out. A cobertura das faixas de 80% ficou entre 76,9% e 78,4%; a das faixas de 95%, entre 89,7% e 93,1%. Elas são referências empíricas úteis, mas não garantias probabilísticas formais. Além disso, são marginais: os limites de UF, região e Brasil não necessariamente somam entre si, embora os pontos previstos sejam coerentes.

Na aplicação operacional, a reconciliação de curto prazo realizou ajustes superiores à faixa histórica usual. No Brasil, o ajuste foi de 129,2 casos em uma semana e 551,0 em quatro semanas. Isso não indica erro de programação: revela discordância excepcional entre o ETS direto dos agregados e a persistência das UFs naquele momento. A projeção deve, por isso, ser comunicada como **cenário reconciliado com alerta de alta discordância**, e não como certeza pontual.

## 10. Limitações

1. A série representa notificações hospitalares confirmadas pelo critério adotado, não todas as infecções por VSR.
2. Mudanças em testagem, notificações e vigilância podem afetar comparabilidade entre temporadas, especialmente em 2020 e 2021.
3. A seleção de modelos e da política usou os mesmos 58 cortes formais de validação; ainda falta uma avaliação inteiramente futura e independente.
4. A calibração da covariância do MinT atravessa o período pandêmico e pode não representar perfeitamente o regime posterior.
5. As previsões em 8 e 13 semanas têm incerteza ampla e servem melhor a cenários do que a números exatos.
6. A previsão operacional de julho de 2026 apresentou alerta de ajuste excepcional entre níveis; esse alerta deve acompanhar qualquer comunicação do resultado.

## 11. Conclusão

O estudo demonstrou que é possível construir, com dados públicos e rastreabilidade completa, uma cadeia de previsão semanal de internações por SRAG associada ao VSR em crianças menores de dois anos. A principal conclusão metodológica é que não se deve procurar um modelo único e universal: o desempenho depende do horizonte, do nível geográfico e do objetivo de uso.

ETS amortecido foi útil em curto prazo para séries densas; a referência ingênua sazonal permaneceu competitiva e superior em horizontes maiores; e o MinT não negativo ofereceu o melhor compromisso para uma visão hierárquica operacional em 1 e 4 semanas. O produto final não elimina a incerteza, mas a torna explícita e impede incoerências que poderiam dificultar o uso conjunto de previsões estaduais, regionais e nacionais.

## 12. Reprodutibilidade e evidências

- Notebook completo: `Estudo_Geral_Trabalho_Series_Temporais.ipynb`.
- Tratamento: `TRATAMENTO_DADOS_1_ETAPA/EXPLICACAO_DAS_DECISOES_TRATAMENTO_DADOS_V2.md`.
- Exploração: `ANALISE_EXPLORATORIA_2_ETAPA/EXPLICACAO_DAS_DECISOES_ANALISE_EXPLORATORIA_V2.md`.
- Modelagem: `MODELAGEM_AVALIACAO_3_ETAPA/EXPLICACAO_DAS_DECISOES_MODELAGEM_AVALIACAO_V2.md`.
- Resultados locais consolidados: `/home/thiago/Series-Temporais-Trabalho/execucao_local_vsr/saidas/etapa_40_consolidacao_final/`.

## Referências metodológicas

- Hyndman, R. J. et al. [Optimal combination forecasts for hierarchical time series](https://collaborate.robjhyndman.com/publications/hierarchical/), 2011.
- Wickramasuriya, S. L., Athanasopoulos, G. e Hyndman, R. J. [Optimal forecast reconciliation for hierarchical and grouped time series through trace minimization](https://robjhyndman.com/papers/MinT.pdf), 2019.
- Hyndman, R. J. e Athanasopoulos, G. [Forecasting: Principles and Practice — Hierarchical forecasting](https://otexts.robjhyndman.com/fpp2/hierarchical-forecasting.html).
