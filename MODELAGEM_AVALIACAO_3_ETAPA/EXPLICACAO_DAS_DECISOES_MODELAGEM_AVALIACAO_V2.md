# Decisões da modelagem e avaliação de previsões — V2

## Objetivo desta etapa

Esta etapa transforma o painel semanal maduro e os achados exploratórios em previsões avaliadas fora da amostra. O objetivo não é escolher o modelo mais complexo: é identificar previsões úteis para antecipar internações por VSR, com comparação justa, reprodutível e compatível com a estrutura geográfica dos dados.

Inicialmente, a avaliação foi feita para Brasil e cinco regiões, que possuem séries mais densas. Em seguida, a estrutura foi ampliada para as 27 Unidades da Federação (UFs), sem ignorar a intermitência de parte delas. Assim, a modelagem passa a responder a duas perguntas diferentes: qual modelo prevê melhor cada horizonte e como tornar previsões de UF, região e Brasil coerentes entre si.

## Reprodução local e princípios de validação

Os resultados documentados abaixo foram reproduzidos localmente em 08/11/2026, no diretório de execução separado do repositório: `/home/thiago/Series-Temporais-Trabalho/execucao_local_vsr`. A separação preserva o projeto versionado e, ao mesmo tempo, permite guardar os arquivos intermediários, auditorias e resultados pesados sem depender de créditos ou do armazenamento temporário do Colab.

O ambiente local utilizou Python 3.13.18, pandas 3.1.1, pyarrow 26.0.1 e statsmodels 0.15.0. Os mesmos microdados congelados, a mesma regra de maturidade de 13 semanas e o mesmo calendário temporal foram usados em todos os modelos comparados.

Os princípios adotados são os seguintes:

1. Cada previsão usa somente informações disponíveis até sua data de origem.
2. Todos os modelos de uma comparação recebem o mesmo painel, os mesmos cortes e os mesmos horizontes.
3. A cobertura é requisito para entrar no ranking: não é adequado declarar vencedor um modelo avaliado em menos cortes que os demais.
4. MAE e RMSE permanecem em número de casos; MASE permite comparar Brasil e regiões, que têm escalas muito distintas.
5. Convergência, previsões negativas, viés e coerência territorial são diagnósticos tão importantes quanto o erro médio.
6. A escolha pode variar por horizonte. Não há justificativa para exigir que um único modelo seja o melhor para uma, quatro, oito e treze semanas.

## Entrada adotada

- Painel de origem: `painel_vsr_semanal_com_maturidade.parquet`.
- Unidade prevista: número semanal de internações por SRAG associadas ao VSR em crianças menores de dois anos.
- Período maduro: 30/12/2018 a 19/07/2026.
- Séries inicialmente modeladas: Brasil e cinco regiões.
- Comprimento de cada série densa: 395 semanas maduras.
- Calendário temporal: 58 origens por série e horizontes de 1, 4, 8 e 13 semanas.

Em cada modelo não hierárquico, isso corresponde a 6 séries × 58 origens × 4 horizontes = 1.392 previsões. Esse número será usado como referência de cobertura.

## Etapa 20 — Preparação das entradas para previsão

Esta etapa confirmou que o painel e o calendário de validação realmente representam o mesmo problema de previsão. O painel completo possui linhas recentes ainda não maduras; elas foram preservadas, mas não foram transformadas em zeros nem usadas no treino ou na avaliação. Isso evita tratar atraso de notificação como ausência de casos.

O recorte aprovado contém 2.370 linhas: seis séries e 395 semanas maduras por série. Não há duplicidade na chave `nível + unidade + semana`, casos negativos ou valores ausentes de `casos_vsr` no recorte de modelagem. O Brasil totaliza 155.304 casos maduros, exatamente a soma das cinco regiões.

Também foram verificados os 1.392 alvos do calendário. Todos estão presentes no painel maduro, possuem o indicador de maturidade verdadeiro e coincidem exatamente com o valor observado associado a cada data-alvo.

**Decisão.** A entrada foi aprovada para baselines e modelos. As UFs não foram excluídas; foram reservadas para a etapa hierárquica, onde sua intermitência poderá ser tratada explicitamente.

## Etapa 21 — Referências simples de previsão

As referências simples estabelecem o desempenho mínimo que um modelo mais complexo precisa superar. A referência ingênua repete o último valor conhecido na origem e representa persistência de curtíssimo prazo. A referência ingênua sazonal recupera a observação da mesma semana epidemiológica do ano anterior.

O método sazonal usou `ano_epi` e `semana_epi`, em vez de simplesmente subtrair 52 semanas. Essa escolha evita desalinhamentos em anos epidemiológicos com 53 semanas. A auditoria confirmou que nenhuma referência sazonal usou informação posterior à origem e que as duas referências produziram as 1.392 previsões esperadas.

![Exemplo das referências no último corte temporal do Brasil](resultados_scripts/etapa_21_referencias_simples/exemplo_previsao_referencias_brasil.png)

No último corte nacional, a referência ingênua repetiu 1.328 casos em todos os horizontes. A referência sazonal recuperou o perfil da temporada anterior e previu 2.499, 2.629, 2.158 e 942 casos para 1, 4, 8 e 13 semanas. Os observados foram 1.386, 1.984, 1.946 e 892. O exemplo não decide o vencedor, mas mostra por que persistência e sazonalidade carregam informações diferentes.

**Decisão.** As referências ingênua e ingênua sazonal foram aprovadas como baselines oficiais do estudo.

## Etapa 22 — Métricas das referências

MAE expressa o erro absoluto médio em casos. RMSE dá mais peso a erros grandes, especialmente importantes quando há risco de pressão hospitalar. MASE divide o erro por uma escala sazonal calculada dentro do treino de cada origem, tornando possível comparar Brasil e regiões sem que a escala da série nacional domine a análise.

Foram calculadas 348 escalas MASE — uma para cada combinação de série e origem — sempre usando somente semanas disponíveis até aquela data. Todas foram positivas e válidas.

![Comparação das referências simples por horizonte](resultados_scripts/etapa_22_metricas_referencias/comparacao_metricas_referencias.png)

| Horizonte | Ingênuo: MASE | Sazonal: MASE | Melhor referência |
|---|---:|---:|---|
| 1 semana | 0,554 | 1,610 | Ingênuo |
| 4 semanas | 1,720 | 1,670 | Sazonal |
| 8 semanas | 3,001 | 1,741 | Sazonal |
| 13 semanas | 4,338 | 1,823 | Sazonal |

O MAE ingênuo cresce de 25,6 casos em uma semana para 229,9 em 13 semanas. O MAE sazonal é maior em uma semana, 87,9, mas permanece próximo de 90 casos de quatro a 13 semanas. A leitura é epidemiologicamente coerente: repetir o último nível pode ser suficiente para resposta imediata, mas não acompanha bem uma onda inteira de circulação do VSR.

**Decisão.** Modelos posteriores precisam superar o ingênuo em uma semana e, principalmente, o ingênuo sazonal em oito e 13 semanas.

## Etapa 23 — Tentativa ETS inicial

O primeiro experimento ETS comparou estruturas com sazonalidade anual: ETS sazonal aditivo, ETS com tendência aditiva e ETS com tendência aditiva amortecida. A ideia era representar nível, possível tendência recente e o padrão anual de VSR.

A primeira implementação estimava simultaneamente os estados sazonais iniciais, nível e tendência. Esse procedimento mostrou instabilidade numérica em alguns cortes, apesar de as seis séries não terem lacunas temporais. Como o período sazonal é longo, 52 semanas, os cortes iniciais contêm apenas cerca de três ciclos anuais completos; estimar muitos estados sazonais junto com os demais parâmetros torna a otimização mais delicada.

Esta tentativa é preservada no histórico metodológico porque motivou uma revisão de implementação. Ela não entra no ranking local final: a evidência comparável e reproduzida localmente começa na Etapa 23B.

**Decisão.** A estrutura conceitual ETS foi mantida, mas a inicialização sazonal foi modificada antes da comparação formal.

## Etapa 23B — ETS com inicialização sazonal heurística

Mantivemos séries, cortes, horizontes e estruturas ETS. A única mudança foi a inicialização heurística dos componentes sazonais: valores iniciais plausíveis são derivados da história observada antes da otimização dos parâmetros restantes. Essa mudança busca separar um problema numérico de um problema substantivo do modelo.

Os 1.044 ajustes esperados convergiram na primeira tentativa: 348 para cada configuração. Cada ETS produziu 1.392 previsões, permitindo comparação justa com as referências.

| Modelo | Ajustes convergentes | Previsões | Previsões corrigidas para zero |
|---|---:|---:|---:|
| ETS sazonal aditivo | 348/348 | 1.392 | 41 (2,9%) |
| ETS tendência aditiva | 348/348 | 1.392 | 226 (16,2%) |
| ETS tendência amortecida | 348/348 | 1.392 | 99 (7,1%) |

Previsões negativas foram convertidas para zero exclusivamente como proteção operacional: contagens de internação não podem ser negativas. Essa correção é também um diagnóstico. A alta frequência no ETS com tendência aditiva indica extrapolação pouco plausível, sobretudo nos horizontes maiores.

![ETS com inicialização heurística no último corte do Brasil](resultados_scripts/etapa_23b_ets_inicializacao_heuristica/exemplo_previsoes_ets_heuristico_brasil.png)

**Decisão.** Os três ETS foram aceitos para a comparação de métricas por possuírem cobertura completa, mas a frequência de correções passou a compor a decisão de elegibilidade.

## Etapa 24 — Comparação entre baselines e ETS

As duas baselines e os três ETS heurísticos foram avaliados nos mesmos 348 cortes, seis séries, quatro horizontes e alvos observados. Cada modelo produziu 1.392 previsões; portanto, diferenças de desempenho não são consequência de cobertura desigual.

![Comparação entre baselines e ETS](resultados_scripts/etapa_24_comparacao_baselines_ets/comparacao_baselines_ets_metricas.png)

| Horizonte | Melhor modelo por MASE | MASE | MAE |
|---|---|---:|---:|
| 1 semana | ETS tendência amortecida | 0,507 | 21,6 |
| 4 semanas | ETS tendência amortecida | 1,311 | 65,5 |
| 8 semanas | Ingênuo sazonal | 1,741 | 89,8 |
| 13 semanas | Ingênuo sazonal | 1,823 | 89,1 |

Em uma semana, o ETS amortecido reduziu o MASE de 0,554 do ingênuo para 0,507. Em quatro semanas, reduziu o melhor MASE de baseline, 1,670, para 1,311. Em oito e 13 semanas, a sazonalidade anual venceu: o ingênuo sazonal foi o melhor nas seis séries.

O ETS com tendência aditiva não venceu nenhum horizonte agregado e exibiu muitas correções para zero: 23,0% em oito semanas e 24,7% em 13 semanas. O ETS sazonal aditivo foi estável, mas não venceu no agregado. O ETS amortecido seguirá como candidato de curto prazo, com ressalva de 6,0% de correções em quatro semanas e 10,3% em 13 semanas.

**Decisão.** A política preliminar passa a depender do horizonte: ETS amortecido é a referência a superar em 1 e 4 semanas; ingênuo sazonal é a referência a superar em 8 e 13 semanas.

## Etapa 25 — SARIMA sazonal clássico

SARIMA foi testado para verificar se dependência serial e sazonalidade anual, modeladas explicitamente, acrescentariam informação além de ETS e baselines. Foram definidas duas especificações parcimoniosas antes da execução, sem busca automática ampla:

- `SARIMA(0,0,1)(0,1,1,52)`, identificado como SARIMA sazonal MA;
- `SARIMA(0,1,1)(0,1,1,52)`, identificado como SARIMA mudança de nível.

A grade pequena foi intencional. Com 395 semanas, um ciclo sazonal de 52 semanas e 348 ajustes por configuração, uma busca ampla aumentaria muito o custo computacional e o risco de selecionar parâmetros excessivamente adaptados ao período avaliado.

Na reprodução local, os modelos não atingiram a cobertura necessária:

| Modelo | Ajustes convergentes | Cobertura de previsões | Situação |
|---|---:|---:|---|
| SARIMA sazonal MA | 279/348 | 1.116/1.392 (80,2%) | Reprovado |
| SARIMA mudança de nível | 282/348 | 1.128/1.392 (81,0%) | Reprovado |

As falhas ocorreram em diversas séries e em várias origens, não apenas nos primeiros treinos. A auditoria registra principalmente não convergência do otimizador de máxima verossimilhança; portanto, aumentar cegamente o número de iterações não seria uma solução metodologicamente defensável.

![Previsões SARIMA no último corte temporal do Brasil](resultados_scripts/etapa_25_modelos_sarima/exemplo_previsoes_sarima_brasil.png)

**Decisão.** Os SARIMA clássicos não entram no ranking principal. Compará-los com modelos avaliados em 100% dos cortes produziria uma conclusão injusta.

## Etapa 25A — Diagnóstico de estabilidade do SARIMA

Esta etapa não tentou “forçar” os SARIMA a concluir. Ela transformou o problema de convergência em evidência auditável: registrou falhas por data, série, tamanho de treino, mensagem do otimizador e previsão negativa.

![Diagnóstico de estabilidade dos SARIMA](resultados_scripts/etapa_25a_diagnostico_sarima/diagnostico_estabilidade_sarima.png)

A cobertura de aproximadamente 80% é insuficiente para uma comparação de erro que exige os mesmos 348 ajustes e 1.392 previsões por modelo. Assim, os SARIMA são resultados relevantes para a narrativa — foram testados, apresentaram limitações concretas e foram descartados por critério predefinido —, mas não são candidatos operacionais.

**Decisão.** Não haverá nova tentativa de SARIMA sazonal clássico nesta fase. A próxima variação deve resolver uma limitação identificada, e não apenas aumentar complexidade.

## Etapa 25B — SARIMAX harmônico

O SARIMAX harmônico foi incluído como alternativa à sazonalidade anual estimada por 52 estados do SARIMA. A série foi transformada por `log1p`, a sazonalidade anual foi representada por dois pares de harmônicos de Fourier, com período 52,1786 semanas, e a dependência de curto prazo foi representada por ARMA(1,1). Não foi incluído componente sazonal SARIMA.

Em termos práticos, os harmônicos descrevem uma onda anual suave sem exigir que o modelo estime separadamente cada semana do ano. Essa escolha é coerente com a sazonalidade observada de VSR, mas permite variação gradual de nível e reduz a dificuldade numérica do SARIMA clássico.

O modelo `SARIMAX_FOURIER2_ARMA11_LOG1P` convergiu nos 348 ajustes, sem erro de ajuste ou previsão, e gerou as 1.392 previsões esperadas. A estabilidade confirma que a reformulação resolveu o problema computacional; ela não implica, por si só, que o modelo seja o mais preciso.

![SARIMAX harmônico no último corte do Brasil](resultados_scripts/etapa_25b_sarimax_harmonico/exemplo_previsao_sarimax_harmonico_brasil.png)

**Decisão.** O SARIMAX harmônico foi aprovado para a comparação não hierárquica como alternativa estável, sem substituir automaticamente ETS ou a baseline sazonal.

## Etapa 26 — Comparação consolidada dos modelos não hierárquicos

Esta etapa reuniu somente modelos com cobertura completa: ingênuo, ingênuo sazonal, ETS sazonal aditivo, ETS de tendência amortecida e SARIMAX harmônico. São cinco modelos × 1.392 previsões = 6.960 erros individuais comparáveis, todos sem valores ausentes.

O ETS com tendência aditiva foi excluído por excesso de previsões corrigidas para zero e desempenho inferior ao ETS amortecido. Os dois SARIMA clássicos foram excluídos pela cobertura de apenas 80,2% e 81,0%.

![Comparação dos modelos não hierárquicos](resultados_scripts/etapa_26_comparacao_modelos_nao_hierarquicos/comparacao_modelos_nao_hierarquicos.png)

| Horizonte | Melhor modelo | MASE | MAE | Leitura |
|---|---|---:|---:|---|
| 1 semana | ETS tendência amortecida | 0,507 | 21,6 | Melhor resposta imediata. |
| 4 semanas | ETS tendência amortecida | 1,311 | 65,5 | Melhor desempenho de curto prazo. |
| 8 semanas | Ingênuo sazonal | 1,741 | 89,8 | A temporada anterior é mais informativa. |
| 13 semanas | Ingênuo sazonal | 1,823 | 89,1 | A sazonalidade anual domina a previsão mais longa. |

O SARIMAX harmônico foi estável, mas não venceu os horizontes: MASE 0,621, 1,462, 2,256 e 2,654 em 1, 4, 8 e 13 semanas. Ele fica especialmente próximo do segundo lugar em oito e 13 semanas, o que mostra que a representação harmônica contém informação sazonal útil, mas não supera a referência sazonal simples no cenário atual.

**Decisão.** Esta é uma recomendação preliminar, restrita a Brasil e regiões e a modelos não hierárquicos. Ela não encerra a escolha final do estudo: ainda falta avaliar se a reconciliação de previsões melhora ou piora o desempenho e a coerência geográfica.

## Etapa 27 — Estrutura e validação da hierarquia geográfica

Os dados formam uma hierarquia geográfica exata: 27 UFs formam cinco regiões, e as cinco regiões formam o Brasil. Antes de gerar previsões hierárquicas, verificamos se essa relação é verdadeira nos dados históricos e construímos formalmente a matriz de agregação.

A estrutura contém 33 nós: 27 folhas (UFs), cinco agregados (regiões) e uma raiz (Brasil). O painel hierárquico possui 13.035 linhas, equivalentes a 33 nós × 395 semanas maduras. Não há duplicidade de chave ou caso ausente.

| Agregado validado | Semanas comparadas | Diferença máxima | Semanas com diferença |
|---|---:|---:|---:|
| Brasil versus soma das UFs | 395 | 0 | 0 |
| Norte versus suas UFs | 395 | 0 | 0 |
| Nordeste versus suas UFs | 395 | 0 | 0 |
| Centro-Oeste versus suas UFs | 395 | 0 | 0 |
| Sudeste versus suas UFs | 395 | 0 | 0 |
| Sul versus suas UFs | 395 | 0 | 0 |

O calendário de avaliação foi expandido sem mudar origens nem horizontes: 232 combinações de origem e horizonte são aplicadas aos 33 nós, resultando em 7.656 previsões exigidas por modelo. Portanto, qualquer método hierárquico futuro será avaliado nos mesmos tempos e com os mesmos alvos observados.

A expansão também confirmou um ponto importante da análise exploratória: 13 UFs têm mais de 50% de semanas sem casos confirmados. Piauí, Mato Grosso, Tocantins e Alagoas superam 70% de semanas zero. Em contraste, São Paulo apresenta 3,0%. Essa heterogeneidade impede usar o mesmo modelo individual complexo para todas as UFs.

**Decisão.** A hierarquia histórica e o calendário hierárquico foram aprovados. Isso demonstra que os dados agregados são coerentes; ainda não demonstra que as previsões serão coerentes. A coerência preditiva será avaliada por métodos de reconciliação.

## Conclusões provisórias

1. A base madura e o calendário temporal permitem comparação reprodutível sem vazamento de informação futura.
2. ETS com tendência amortecida é a melhor referência para previsões de uma e quatro semanas em Brasil e regiões.
3. A referência ingênua sazonal é difícil de superar em oito e 13 semanas; ela deve permanecer como baseline obrigatório.
4. A inicialização heurística resolveu a instabilidade do ETS sem alterar a definição do problema de previsão.
5. Os SARIMA clássicos não atingiram cobertura suficiente e foram descartados de forma transparente.
6. O SARIMAX harmônico entregou estabilidade completa, mas não superou os melhores métodos nos horizontes avaliados.
7. A escolha não hierárquica atual é preliminar e depende do horizonte.
8. A hierarquia geográfica histórica é exata, mas a alta intermitência em várias UFs exige uma reconciliação cuidadosa e avaliação por nível geográfico.

## Próximos passos aprovados

1. Gerar previsões-base para os 33 nós geográficos. Para Brasil e regiões, a política será guiada pelo resultado não hierárquico; para UFs intermitentes, começaremos com referências sazonais estáveis.
2. Construir erros de calibração anteriores ao período formal de validação, evitando usar alvos futuros para estimar a incerteza da reconciliação.
3. Comparar previsões-base, bottom-up, top-down, reconciliação estrutural e MinT com shrinkage, caso os diagnósticos de covariância permitam.
4. Avaliar os resultados separadamente em Brasil, regiões e UFs. Uma média global não deve ocultar o desempenho nos níveis operacionais mais relevantes.
5. Auditar previsões negativas. Truncar valores após uma reconciliação pode quebrar a coerência da soma; se esse problema for material, a reconciliação deverá incorporar não negatividade ou ser descartada.

## Referências metodológicas

- Hyndman, R. J. et al. *Optimal combination forecasts for hierarchical time series* (2011): https://collaborate.robjhyndman.com/publications/hierarchical/
- Wickramasuriya, S. L., Athanasopoulos, G. e Hyndman, R. J. *Optimal forecast reconciliation for hierarchical and grouped time series through trace minimization* (2019): https://robjhyndman.com/papers/MinT.pdf
- Hyndman, R. J. e Athanasopoulos, G. *Forecasting: Principles and Practice — Hierarchical forecasting*: https://otexts.robjhyndman.com/fpp2/hierarchical-forecasting.html
- Statsmodels. *SARIMAX*: https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html

## Arquivos de evidência

- Notebook da etapa: `notebook_parcial_modelagem_avaliacao/Modelagem_Avaliacao_3_Etapa_v2.ipynb`.
- Etapa 20: `resultados_scripts/etapa_20_preparacao_modelagem/`.
- Etapas 21 e 22: `resultados_scripts/etapa_21_referencias_simples/` e `resultados_scripts/etapa_22_metricas_referencias/`.
- Etapa 23B: `resultados_scripts/etapa_23b_ets_inicializacao_heuristica/`.
- Etapa 24: `resultados_scripts/etapa_24_comparacao_baselines_ets/`.
- Etapas 25 e 25A: `resultados_scripts/etapa_25_modelos_sarima/` e `resultados_scripts/etapa_25a_diagnostico_sarima/`.
- Etapa 25B: `resultados_scripts/etapa_25b_sarimax_harmonico/`.
- Etapa 26: `resultados_scripts/etapa_26_comparacao_modelos_nao_hierarquicos/`.
- Etapa 27: `resultados_scripts/etapa_27_estrutura_hierarquica/`.
