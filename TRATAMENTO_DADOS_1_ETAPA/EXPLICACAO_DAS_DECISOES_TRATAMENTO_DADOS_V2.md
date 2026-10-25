# Decisões do tratamento de dados — V2

## Objetivo desta etapa
Este documento registra as decisões tomadas para transformar microdados de SRAG do SIVEP-Gripe em uma base individual confiável de internações associadas ao VSR em crianças menores de dois anos.
Ainda não há modelagem ou previsão aqui. O objetivo é criar uma única base auditável que será usada de forma igual por todos os modelos.

## Fonte e versão dos dados
- Fonte primária: [SIVEP-Gripe / OpenDataSUS](https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026).
- Foram usados oito arquivos Parquet anuais, de 2019 a 2026, verificados por URL, tamanho e SHA-256 antes da leitura.
- Os arquivos de 2019–2024 têm data de publicação no nome de 23/03/2026; os de 2025–2026, de 19/10/2026.
- O ano de 2026 é parcial: o último início de sintomas observado é 18/10/2026. Ele será usado com cuidado nas etapas futuras.

## Princípios adotados
1. Não usar informação futura para definir ou avaliar previsões.
2. Não tratar ausência de exame específico para VSR como resultado negativo.
3. Preservar rastreabilidade: cada filtro, exceção e deduplicação produz um arquivo de auditoria.
4. Diferenciar o que os dados mostram do que é apenas uma hipótese metodológica.

## Etapa 1 — Preparação do ambiente
**O que foi feito.** Foram criadas pastas separadas para dados brutos, intermediários, tratados e saídas do notebook.
**Por quê.** A separação evita sobrescrever a fonte original e permite reproduzir cada resultado.
**Objetivo.** Organizar o estudo antes de qualquer leitura ou transformação de dados.

## Etapa 2 — Localização e congelamento da fonte
**O que foi feito.** A API e a listagem pública do OpenDataSUS/S3 apresentaram instabilidade ou bloqueio de acesso. Em vez de abandonar a fonte, foram verificadas URLs diretas de arquivos oficiais por ano.
**Por quê.** Os microdados podem ser republicados; nomes e versões mudam. Uma previsão só é reproduzível se a versão consultada ficar registrada.
**Decisão.** Usar os oito arquivos oficiais validados, sem alegar que representam necessariamente a versão mais recente do portal no futuro.

## Etapa 3 — Download e integridade
**O que foi feito.** Os arquivos foram baixados individualmente, com registro de tamanho esperado, tamanho obtido, URL, momento do download e SHA-256.
**Evidência.** Os oito arquivos tiveram tamanhos esperados e baixados idênticos; o total foi 333,67 MB.
**Objetivo.** Garantir que a análise não comece com arquivo incompleto, corrompido ou de origem desconhecida.

## Etapa 4 — Inspeção estrutural
**O que foi feito.** Foram lidos metadados dos Parquet sem carregar todos os registros individuais.
**Evidência.** Há 4.679.012 notificações brutas e exatamente 194 colunas em todos os anos de 2019 a 2026.
**Decisão.** A estrutura é suficientemente homogênea para uma base única; diferenças de tipo, como em `CLASSI_FIN`, serão normalizadas quando necessário.

## Etapa 5 — Inventário completo e qualidade dos campos
**O que foi feito.** Todas as 194 colunas foram inventariadas por nome, tipo e ausência. Depois, campos epidemiológicos e laboratoriais foram diagnosticados sem excluir registros.
**Por quê.** Siglas semelhantes não bastam para definir uma variável. Primeiro se identifica toda a estrutura; depois se confirma a função de cada campo relevante.
**Achados principais.** `DT_SIN_PRI`, `NU_IDADE_N`, `TP_IDADE`, `SEM_PRI` e `SEM_NOT` não têm ausência. `DT_INTERNA` contém datas implausíveis e não será o relógio principal da série.

## Etapa 6 — Diagnóstico do recorte epidemiológico
**Data.** `DT_SIN_PRI` foi escolhida como referência temporal provisória, pois representa o início de sintomas, está completa e apresenta intervalo coerente com os arquivos anuais.
**Geografia.** `SG_UF` foi adotada como UF de residência provisória: tem ausência menor que 0,1% e acompanha o município de residência. `SG_UF_INTE` perde de 5,8% a 12,7% dos registros.
**Idade.** Os códigos observados são compatíveis com 1=dias, 2=meses e 3=anos. A idade será convertida para meses antes do filtro.
**VSR.** Os únicos marcadores específicos considerados para confirmação são `PCR_VSR = 1` e `AN_VSR = 1`.

## Etapa 7 — Validação das regras antes do filtro
**O que foi feito.** Foram testadas coerência laboratorial, valores de idade, códigos de UF, hospitalização e duplicidades no recorte provisório.
**Evidências.** Foram encontrados apenas 21 valores de idade negativos e nenhum código de UF inválido. `HOSPITAL = 1` representa 94% a 98% dos registros anuais.
**Decisão.** O recorte estrito exige: idade válida menor que 24 meses, UF válida, `HOSPITAL = 1` e confirmação de VSR por PCR ou antígeno.
**Limite importante.** A cobertura de VSR específico varia muito entre anos; a série resultante mede VSR confirmado, e não o total real de VSR na população.

## Etapa 8 — Base individual e deduplicação
**O que foi feito.** Foi criada a base individual de casos elegíveis e investigadas duas notificações duplicadas com datas de sintomas diferentes.
**Decisão de deduplicação.** Para a mesma notificação, foi escolhida a versão com a menor defasagem não negativa entre sintomas e notificação. Nos dois grupos, a versão de 2025 foi mais coerente que a versão de 2024.
**Evidência.** Antes da deduplicação havia 158.360 linhas; duas foram removidas. A base final possui 158.358 notificações e nenhuma duplicidade remanescente.
**Auditoria laboratorial.** A base preserva se a confirmação ocorreu por PCR, antígeno ou ambos; os métodos não foram confundidos nem contados duas vezes.

## Regra final da base individual
Um registro entra na base se atender simultaneamente a:
1. `DT_SIN_PRI` válida;
2. idade convertida em meses entre 0 e menor que 24;
3. `SG_UF` correspondente a uma das 27 Unidades da Federação;
4. `HOSPITAL = 1`;
5. `PCR_VSR = 1` ou `AN_VSR = 1`;
6. uma única versão por `NU_NOTIFIC`, após a regra temporal de deduplicação.

## Etapa 9 — Painel semanal e hierarquia geográfica
**O que foi feito.** Os 158.358 casos individuais foram agregados pela semana de início de sintomas, primeiro nas 27 UFs e depois nas 5 regiões e no Brasil.
**Evidência.** O painel tem 407 semanas, de 30/12/2018 a 11/10/2026, e 13.431 linhas: 10.989 de UF, 2.035 de região e 407 do Brasil.
**Decisão.** A última semana foi mantida como parcial e recebeu `NaN`, não zero. A soma das UFs coincide exatamente com o total do Brasil em todas as semanas fechadas.

## Etapa 10 — Atraso de disponibilidade
**O que foi feito.** A base individual foi enriquecida com a data em que cada caso de VSR se tornou disponível: a data mais tardia entre o registro e o resultado laboratorial aplicável.
**Evidência.** Todos os 158.358 casos receberam data de disponibilidade e não houve atraso negativo. A mediana anual ficou entre 8 e 13 dias; o percentil 95 anual máximo foi 86 dias, em 2021.
**Decisão.** Semanas recentes devem ser tratadas como potencialmente incompletas, mesmo quando já possuem alguma contagem observada.

## Etapa 11 — Maturidade das semanas
**O que foi feito.** Foi marcado um indicador de maturidade sem apagar os valores observados.
**Decisão.** Uma semana é madura se está fechada e tem ao menos 13 semanas até o corte da fonte, publicado em 19/10/2026. O limiar é conservador: o P95 global foi 50 dias, mas o pior P95 anual exigiu 13 semanas.
**Evidência.** Há 395 semanas maduras, que concentram 155.304 casos, e 12 semanas recentes ou incompletas, com 3.046 casos observados. A última semana, 11/10/2026, permanece sem contagem final.

## Estado atual e próximo passo
O tratamento de dados foi concluído. As saídas principais são a base individual `casos_vsr_menores2.parquet`, sua versão com disponibilidade e o painel `painel_vsr_semanal_com_maturidade.parquet`.
Os modelos deverão ser treinados e avaliados apenas com semanas maduras; as semanas recentes serão usadas para previsão corrente ou para métodos futuros de correção de atraso.

## Arquivos de evidência
- Notebook parcial: `notebook_parcial_tratamento_dados.ipynb/Estudo_Geral_Trabalho_Series_Temprais.ipynb`.
- Resultados e auditorias: `resultados_scripts/`.
- Manifesto de download: `resultados_scripts/manifesto_download_srag.csv`.
- Auditoria da base final: `resumo_base_individual_final.csv`, `auditoria_escolhas_duplicidade.csv` e `auditoria_metodo_confirmacao_final.csv`.
- Auditoria do painel: `resumo_painel_semanal.csv`, `validacao_hierarquia_painel.csv` e `validacao_limiar_maturidade.csv`.
