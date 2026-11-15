# Ordem de leitura e estudo

Atualização: 14/11/2026. Preparação para segunda-feira, 16/11/2026.

## Primeiro percurso — entender o trabalho

1. [Guia pessoal de Thiago](GUIA_PESSOAL_THIAGO.md): leia inteiro primeiro; esclarece os nomes e a história.
2. [Explicação inicial](EXPLICACAO_INICIAL_ST.md): entenda a pergunta original; observe a nota sobre SINASC não utilizado.
3. [Tratamento](../TRATAMENTO_DADOS_1_ETAPA/EXPLICACAO_DAS_DECISOES_TRATAMENTO_DADOS_V2.md): explique recorte, residência, sintomas, duplicidades e maturidade.
4. [Análise exploratória](../ANALISE_EXPLORATORIA_2_ETAPA/EXPLICACAO_DAS_DECISOES_ANALISE_EXPLORATORIA_V2.md): entenda por que sazonalidade, mudanças de nível e zeros motivaram os testes.
5. [Guia de modelos](ENTENDIMENTO_TIPOS_MODELOS_IMPORTANTES_PARA_ESTUDO.md): leia as fichas clássicas como primeira rodada; depois as fichas 6–8 e a política vigente.
6. [Narrativa das decisões](NARRATIVA_DAS_DECISOES.md): acompanhe a evolução até 40 e a extensão 41–43.
7. [Decisões da modelagem](../MODELAGEM_AVALIACAO_3_ETAPA/EXPLICACAO_DAS_DECISOES_MODELAGEM_AVALIACAO_V2.md): confirme os detalhes; as conclusões anteriores a 41 são históricas.
8. [Relatório final](RELATORIO_FINAL.md): consolide método, números vigentes e limitações.
9. [Conclusão epidemiológica](CONCLUSAO_EPIDEMIOLOGICA.md): prepare o que os resultados permitem dizer em saúde.
10. Volte ao guia pessoal e explique a política sem consultar a tabela.

## Segundo percurso — acompanhar o código

A numeração 01–06 identifica arquivos; 1–43 identifica etapas dentro deles.

| Arquivo | Etapas | O que estudar |
|---|---|---|
| [01 Tratamento](../TRATAMENTO_DADOS_1_ETAPA/01_Tratamento_Dados.ipynb) | 1–11 | Da fonte ao painel maduro |
| [02 Exploração](../ANALISE_EXPLORATORIA_2_ETAPA/02_Analise_Exploratoria.ipynb) | 12–19 | Padrões e calendário de avaliação |
| [03 Modelagem](../MODELAGEM_AVALIACAO_3_ETAPA/03_Modelagem_Avaliacao.ipynb) | 20–40 | Clássicos, hierarquia e política anterior |
| [04 Intermitência](../MODELAGEM_AVALIACAO_3_ETAPA/04_Modelos_Intermitentes_UFs.ipynb) | 41 | Candidatos para UFs e Base V3 |
| [05 LightGBM global](../MODELAGEM_AVALIACAO_3_ETAPA/05_LGBM_Global_vs_ETS.ipynb) | 42 | Modelo de 33 nós e Base V4 |
| [06 Política final](../MODELAGEM_AVALIACAO_3_ETAPA/06_Politica_Final.ipynb) | 43 | Combinação vigente, incerteza e diagnóstico |

Leia as explicações e saídas antes de executar. Não é preciso rodar horas de SARIMA para estudar resultados já salvos.

## Conferência final antes de apresentar

- A tabela vigente tem MinT não negativo em todos os horizontes.
- Os números finais vêm da pasta da etapa 43.
- Base V2 independente e política V2 anterior não são o mesmo comparador.
- A política final usa V3 em 1/4 e V4 em 8/13.
- Não houve ganho em todas as combinações: região em h=13 piorou levemente.
- A origem demonstrativa é julho de 2026 e as contagens usam semana de sintomas.
- Artigo/PDF/slides devem ser conferidos contra esses números antes da apresentação; esta atualização não recompilou esses artefatos.
