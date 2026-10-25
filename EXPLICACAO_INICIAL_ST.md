# Explicação inicial — Trabalho de Séries Temporais

## Problema proposto
O vírus sincicial respiratório (VSR) é uma causa importante de doenças respiratórias em crianças pequenas. Em determinados períodos do ano, ele pode aumentar a procura por atendimento e por internações pediátricas, mas esse aumento não ocorre da mesma forma nem no mesmo momento em todo o Brasil.

Nosso trabalho parte de uma pergunta simples: é possível acompanhar os registros já disponíveis e identificar, com alguma antecedência, quando e onde a demanda por internações associadas ao VSR tende a crescer? O foco está em crianças menores de dois anos e na comparação entre Unidades da Federação, regiões e o país como um todo.

## Como pensamos em conduzir o trabalho
Primeiro, vamos organizar os registros oficiais em uma visão semanal, para observar a evolução das internações ao longo do tempo. Em seguida, vamos entender os padrões que aparecem nos dados: períodos de maior e menor ocorrência, diferenças entre regiões e alterações que possam ser explicadas por atrasos de notificação.

A etapa seguinte será transformar essa leitura dos dados em estimativas de curto prazo, sempre verificando se elas se confirmam quando chegam novas semanas de informação. A proposta é construir o estudo de forma transparente, documentando as decisões, as limitações e os resultados que realmente se sustentam nos dados.

## Bases de dados utilizadas
- **SIVEP-Gripe / OpenDataSUS:** microdados oficiais de Síndrome Respiratória Aguda Grave (SRAG), incluindo data de início dos sintomas, idade, local de residência e resultado laboratorial para VSR. Essa é a fonte principal das internações analisadas.
  Fonte: [SRAG 2019–2026 — OpenDataSUS](https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026).
- **SINASC / DATASUS:** registros de nascidos vivos, usados como referência complementar para contextualizar o tamanho da população infantil em cada local e período.
  Fonte: [Transferência de Arquivos — DATASUS](https://datasus.saude.gov.br/transferencia-de-arquivos/).

## Possíveis ganhos para a sociedade brasileira
Conhecer com mais clareza a dinâmica regional do VSR pode ajudar a tornar visíveis períodos de maior pressão sobre serviços pediátricos, em vez de depender apenas de uma visão nacional ou de calendários fixos.

Se os resultados forem consistentes em novas verificações, eles poderão apoiar discussões sobre preparação de leitos, equipes, testes e ações de prevenção nos locais e semanas de maior demanda. O estudo também valoriza o uso responsável de dados públicos e pode servir de base para novas pesquisas sobre vigilância de doenças respiratórias no Brasil.

Esses ganhos são potenciais. Qualquer uso em decisões operacionais ou políticas públicas exigirá validação adicional, avaliação epidemiológica e participação dos gestores do SUS.
