# Relatório final — Previsões hierárquicas de SRAG associada ao VSR

Disciplina: IND2616 — Séries Temporais, PUC-Rio. Professor: Fernando Cyrino.
Autores: Thiago Paes, Joan Souza, Matheus Accioly e Isabelle Gagno.

Versão documental: 14/11/2026. Abrange etapas 1–43 na branch `reorganizacao-reprodutivel`.
As etapas 37–40 registram a primeira política; a decisão vigente está na etapa 43.

## Resumo

O estudo organiza notificações hospitalares de SRAG com confirmação de VSR em crianças menores de dois anos e compara previsões semanais em 27 UFs, cinco regiões e Brasil. Após tratamento e análise exploratória, foram avaliados modelos clássicos, métodos de intermitência e LightGBM global, seguidos de reconciliação hierárquica. A extensão das etapas 41–43 melhorou o MASE em 11 das 12 combinações de nível e horizonte frente à política anterior. Regiões em 13 semanas tiveram pequena piora. A conclusão é condicionada ao desenho retrospectivo e à reutilização das origens para seleção.

## Problema e unidade prevista

A pergunta é se o histórico permite antecipar contagens semanais de casos hospitalizados confirmados, respeitando as somas UF → região → Brasil. A contagem é organizada pela semana de início de sintomas e pela UF de residência. Portanto, não mede diretamente admissões na semana de entrada no hospital, ocupação de leitos ou internações no local do estabelecimento. Não se estima incidência populacional: faltam denominadores e a cobertura de testagem pode variar.

## Fonte e tratamento — etapas 1–11

Fonte: [SIVEP-Gripe / OpenDataSUS](https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026).
Foram usados oito Parquet oficiais, 2019–2026, totalizando 333,67 MB, 4.678.812 notificações brutas e 194 campos. Os arquivos de 2019–2024 têm publicação de 23/03/2026 no nome; os de 2025–2026, 19/10/2026. O manifesto registra URLs, tamanhos e SHA-256.

O recorte exige idade válida de zero a menos de 24 meses, `HOSPITAL = 1`, UF de residência válida, início de sintomas válido e `PCR_VSR = 1` ou `AN_VSR = 1`. Ausência de exame não foi convertida em resultado negativo. SINASC foi mencionado no planejamento inicial, mas não alimentou os modelos executados.

Duas notificações duplicadas, com quatro versões, foram investigadas. A deduplicação priorizou coerência temporal entre sintomas e notificação, seguida de critérios de atualização. Duas linhas foram removidas: restaram 158.358 notificações.

O painel tem 407 semanas e 13.431 linhas (33 nós × 407). A última semana parcial permanece sem contagem final; ausência não foi convertida em zero. As somas geográficas foram verificadas.

A disponibilidade considerou registro e resultado laboratorial. O P95 global de atraso foi 50 dias; o maior P95 anual, 86 dias. Adotaram-se 13 semanas de maturidade até o corte da fonte de 19/10/2026. Há 395 semanas maduras, de 30/12/2018 a 19/07/2026, com 155.304 casos.

## Exploração — etapas 12–19

A exploração identificou sazonalidade, dependência de curto prazo e diferenças regionais. Os picos brasileiros nas temporadas completas ocorreram entre as semanas epidemiológicas 11 e 19. O aumento observado após 2022 não permite separar mudanças de circulação, testagem e notificação.

Treze UFs apresentam mais de 50% de semanas maduras com zero. O percentual de zeros descreve a série registrada, não demonstra ausência de circulação viral. Nível e variabilidade mudam entre temporadas; 2020 e 2021 foram mantidos, com interpretação cautelosa.

O calendário usa 58 origens expansivas, de 19/12/2021 a 19/04/2026, com pelo menos 156 semanas iniciais e horizontes de 1, 4, 8 e 13 semanas. São 1.392 previsões por método nas seis séries agregadas e 7.656 na hierarquia inteira.

## Modelos clássicos e primeira política — etapas 20–40

As referências ingênua e ingênua sazonal foram comparadas a suavização exponencial e modelos ARIMA. ETS com tendência amortecida e sazonalidade aditiva de 52 semanas foi selecionado para agregados em horizontes curtos. A inicialização heurística resolveu o problema de convergência da tentativa anterior.

O SARIMA clássico foi investigado, mas a cobertura insuficiente impediu sua adoção. SARIMAX com harmônicos anuais foi mais estável, sem superar os métodos selecionados. Nas UFs, a referência ingênua venceu em horizontes curtos; a sazonal foi preferida nos longos.

Isso produziu a Base V2. Foram comparados bottom-up, top-down global e sazonal, WLS estrutural, MinT-OAS e MinT não negativo. WLS e MinT irrestritos produziram negativos. A primeira política usou MinT não negativo em 1/4 semanas e a própria Base V2 sazonal em 8/13. Ela é o comparador histórico, não o encerramento atual.

## Extensão — etapas 41 e 42

Na etapa 41 foram avaliados Croston clássico, otimizado e SBA; TSB; ADIDA; IMAPA; TSB sazonal; GLM binomial negativo com Fourier; e LightGBM com perda Tweedie treinado conjuntamente nas 27 UFs. A classificação ADI × CV² é descritiva e utiliza a série completa; não serve como atributo conhecido antecipadamente.

LightGBM das UFs apresentou o menor MASE médio estadual por horizonte na comparação executada. Em 13 semanas, a diferença frente à referência sazonal foi praticamente nula. A Base V3 mantém os agregados da V2 e substitui as previsões estaduais por esse LightGBM.

A etapa 42 treinou LightGBM nos 33 nós, com normalização pela média de treino de cada nó. Foram usados valores recentes, referência sazonal, médias móveis, proporção de zeros e calendário, além de identificadores. Há um modelo direto por horizonte, reajustado em cada origem; os alvos do treino não ultrapassam essa origem. Não foram adicionados clima, mobilidade ou denominadores externos.

A Base V4 selecionou o candidato de menor MASE por nível e horizonte. V4 não equivale à política final: é necessário avaliar novamente após reconciliar, pois o resultado conjunto pode mudar.

## Decisão da etapa 43

| Horizonte | Base escolhida | Brasil | Regiões | UFs | Reconciliação |
|---|---|---|---|---|---|
| 1 e 4 semanas | V3 | ETS amortecido | ETS amortecido | LightGBM treinado conjuntamente nas 27 UFs | MinT-OAS não negativo |
| 8 semanas | V4 | Ingênuo sazonal | LightGBM global de 33 nós | LightGBM global de 33 nós | MinT-OAS não negativo |
| 13 semanas | V4 | Ingênuo sazonal | Ingênuo sazonal | LightGBM global de 33 nós | MinT-OAS não negativo |

Todos os horizontes passam por MinT-OAS não negativo, com covariância calibrada nas 39 origens anteriores à avaliação formal, usando erros dos respectivos modelos-base. A não negatividade é imposta às folhas dentro da otimização; a agregação produz regiões e Brasil coerentes.

V3 reconciliada foi mantida em 1/4 semanas como compromisso. Em h=1, V4 reconciliada tem menor MASE no Brasil (0,274 contra 0,288), mas V3 favorece regiões e UFs. Em h=4, V3 favorece Brasil e regiões, enquanto V4 tem menor MASE nas UFs. Portanto, não há dominância de V3 nos três níveis.

## Desempenho retrospectivo

MASE menor indica menor erro escalonado. A referência “anterior” abaixo é a política da etapa 37, já reconciliada nos horizontes curtos; não é a Base V2 independente.

| Nível | h=1: anterior → atual | h=4: anterior → atual | h=8: anterior → atual | h=13: anterior → atual |
|---|---|---|---|---|
| Brasil | 0,333 → 0,288 | 1,202 → 0,802 | 1,575 → 1,541 | 1,522 → 1,457 |
| Regiões | 0,535 → 0,480 | 1,417 → 1,113 | 1,775 → 1,700 | 1,883 → 1,889 |
| UFs | 1,133 → 1,077 | 2,211 → 1,918 | 2,990 → 2,745 | 3,122 → 3,056 |

Para Brasil em quatro semanas, o MAE passou de 190,5 para 121,9 casos, e o MASE caiu cerca de 33,3%. Isso não significa “33,3% mais acerto” ou efeito em internações reais. É redução da métrica nesse conjunto de avaliação. As médias por nível não significam melhora em todas as UFs individualmente.

## Aplicação demonstrativa, incerteza e plausibilidade

A origem é 19/07/2026, última semana madura, e não a data atual de apresentação. Os horizontes referem-se a uma semana-alvo, não ao acumulado de todas as semanas do intervalo.

| Horizonte | Semana-alvo | Brasil: previsão | Faixa empírica 80% | Faixa empírica 95% |
|---|---|---:|---:|---:|
| 1 | 26/07/2026 | 683,2 | 634,9–756,3 | 553,8–844,8 |
| 4 | 16/08/2026 | 329,2 | 176,7–677,3 | 134,1–941,3 |
| 8 | 13/09/2026 | 190,0 | 6,8–737,2 | 0–1.288,8 |
| 13 | 18/10/2026 | 88,0 | 0–598,0 | 0–1.080,7 |

A etapa 43 gerou 132 pontos (33 × 4). O quadro de alertas está vazio: nenhum ajuste final-base ultrapassou o P95 histórico segundo o diagnóstico implementado. Isso difere dos alertas da antiga etapa 38A, mas não comprova que a nova previsão esteja correta.

As faixas são quantis de resíduos por nó e horizonte. A cobertura LOO média de 80% varia de 75,86% a 79,31%; a de 95%, de 91,38% a 93,10%. São faixas marginais, com subcobertura, sem soma garantida dos limites. O LOO exclui o próprio erro, mas pode usar erros de datas posteriores à origem avaliada: é diagnóstico retrospectivo, não teste operacional prospectivo dos intervalos.

## Limitações e conclusão

A seleção dos modelos e da política reutiliza as mesmas 58 origens usadas para calcular as métricas. Os ganhos podem estar otimistas; a magnitude desse viés não foi estimada. Não há teste final intocado nem demonstração de significância estatística. A calibração do MinT atravessa 2020–2021. A validação usa uma versão consolidada dos registros: separar datas de treino e alvo evita o uso direto de alvos futuros no ajuste, mas não reconstitui exatamente o que estava publicado em cada origem histórica. A maturidade de 13 semanas reduz o problema das semanas recentes; não substitui snapshots históricos ou uma avaliação em tempo real.

A hipótese de que modelos diferentes entre níveis ajudam o MinT é compatível com os resultados, mas não foi isolada em experimento causal. Ausência de alerta de reconciliação não implica validação clínica nem adequação de alocação de leitos.

A contribuição é uma cadeia auditável de dados públicos, modelos comparáveis e previsões geograficamente coerentes. A extensão mostra que aprendizado compartilhado entre séries pode acrescentar informação útil ao conjunto clássico. A política atual deve ser avaliada futuramente em novas semanas maduras, sem nova seleção baseada nos próprios resultados do teste.

## Evidências e leitura

- [Tratamento](../TRATAMENTO_DADOS_1_ETAPA/EXPLICACAO_DAS_DECISOES_TRATAMENTO_DADOS_V2.md).
- [Exploração](../ANALISE_EXPLORATORIA_2_ETAPA/EXPLICACAO_DAS_DECISOES_ANALISE_EXPLORATORIA_V2.md).
- [Modelagem e evolução até 43](../MODELAGEM_AVALIACAO_3_ETAPA/EXPLICACAO_DAS_DECISOES_MODELAGEM_AVALIACAO_V2.md).
- [Quadro de desempenho vigente](../MODELAGEM_AVALIACAO_3_ETAPA/resultados_scripts/etapa_43_politica_final/quadro_desempenho_politica_final.csv).
- [Reprodução](REPRODUTIBILIDADE.md) e [ordem de leitura](ORDEM_DE_LEITURA.md).
