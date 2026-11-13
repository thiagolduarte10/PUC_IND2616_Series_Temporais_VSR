# Previsão hierárquica de internações por VSR (SRAG, menores de 2 anos)

Trabalho da disciplina IND2616 — Séries Temporais (PUC-Rio). Previsão semanal de internações por vírus sincicial
respiratório (SIVEP-Gripe / OpenDataSUS) na hierarquia **Brasil → 5 regiões → 27 UFs** (33 séries), em horizontes de
1, 4, 8 e 13 semanas, com previsões **coerentes** entre os níveis e **não negativas**.

## Resultado final

Política adotada (etapa 43): todos os horizontes reconciliados com **MinT-OAS não negativo**.

| Horizonte | Brasil | Regiões | UFs |
|---|---|---|---|
| 1 e 4 | ETS amortecido | ETS amortecido | LightGBM Tweedie (só UFs) |
| 8 | ingênuo sazonal | LightGBM global | LightGBM global |
| 13 | ingênuo sazonal | ingênuo sazonal | LightGBM global |

MASE médio nas 58 origens de validação (dez/2021 – abr/2026), política anterior (V2, etapa 37) → final (etapa 43):

| Nível | h=1 | h=4 | h=8 | h=13 |
|---|---|---|---|---|
| Brasil | 0,332 → **0,288** | 1,202 → **0,802** | 1,575 → **1,541** | 1,522 → **1,457** |
| Regiões | 0,534 → **0,480** | 1,417 → **1,113** | 1,775 → **1,700** | **1,883** → 1,889 |
| UFs | 1,133 → **1,077** | 2,211 → **1,918** | 2,990 → **2,745** | 3,122 → **3,056** |

Quadros completos: `MODELAGEM_AVALIACAO_3_ETAPA/resultados_scripts/etapa_43_politica_final/`.

## Estrutura

```
TRATAMENTO_DADOS_1_ETAPA/
  01_Tratamento_Dados.ipynb          etapas 1–11: download congelado, recorte, deduplicação, painel semanal, maturidade
ANALISE_EXPLORATORIA_2_ETAPA/
  02_Analise_Exploratoria.ipynb      etapas 12–19: sazonalidade, intermitência das UFs, autocorrelação, calendário de validação
MODELAGEM_AVALIACAO_3_ETAPA/
  03_Modelagem_Avaliacao.ipynb       etapas 20–40: referências, ETS, SARIMA(X), hierarquia, bottom-up, top-down, MinT,
                                     política V2 (37–40 ficam como registro da política anterior)
  04_Modelos_Intermitentes_UFs.ipynb etapa 41: Croston/SBA/TSB/ADIDA/IMAPA, GLM binomial negativo, LightGBM nas UFs
  05_LGBM_Global_vs_ETS.ipynb        etapa 42: LightGBM global (33 nós) contra ETS nos agregados
  06_Politica_Final.ipynb            etapa 43: política final, previsão operacional, plausibilidade, faixas, quadros
*/resultados_scripts/etapa_XX_*/     saídas versionadas de cada etapa (CSV/PNG) — cada notebook grava aqui
*/EXPLICACAO_DAS_DECISOES_*.md       justificativas das decisões de cada fase

src/vsr/                             código compartilhado (pacote instalado com pip install -e .)
  config.py                          caminhos: raiz, dados locais, pasta versionada de cada etapa; versões do ambiente
  dados_srag.py                      catálogo, verificação e download congelado (SHA-256) dos microdados SRAG
  hierarquia.py                      hierarquia de 33 nós, métricas, MinT-OAS não negativo, LightGBM (etapas 41–43)
scripts/
  executar_pipeline.py               executa os notebooks 01→06 e gera as figuras
  comparar_resultados.py             compara os resultados atuais com uma versão do git (reprodutibilidade)

APRESENTACAO_RESULTADOS/             slides de resultados (LaTeX/PDF) e gerar_figuras.py
APRESENTACAO_PARCIAL_27_10_2026/     apresentação parcial
ARTIGO_SBPO/                         artigo (LaTeX/PDF); as figuras vêm de */resultados_scripts/
docs/                                relatório final, narrativa das decisões, conclusão epidemiológica, guia de modelos,
                                     reprodutibilidade
execucao_local_vsr/                  (fora do git) microdados brutos, bases intermediárias e tratadas
```

## Como executar

**1. Ambiente** (Python 3.13; versões fixadas em `requirements.txt`):

```bash
conda env create -f environment.yml
conda activate vsr-st
python -m ipykernel install --user --name vsr-st --display-name "Python 3.13 (vsr-st)"
```

Sem conda: crie um ambiente com Python 3.13 e rode `pip install -r requirements.txt` (instala também o pacote `vsr`
em modo editável).

**2. Dados.** O notebook 01 baixa os oito arquivos Parquet fixados (≈ 330 MB) do repositório oficial do
OpenDataSUS para `execucao_local_vsr/dados_brutos/SRAG/` e registra o SHA-256 de cada um. Se você tiver o pacote
`execucao_local_vsr.zip` de uma execução anterior, extraia-o na raiz: arquivos cujo hash confere com o manifesto são
reaproveitados sem acessar a rede, e um arquivo publicado que tenha mudado é recusado.

**3. Execução** (a partir da raiz, com o ambiente ativo):

```bash
python scripts/executar_pipeline.py              # tudo: 01 → 06 + figuras (≈ 3 h; a etapa 25/SARIMA leva ≈ 2 h 20 min)
python scripts/executar_pipeline.py --de 4       # só a política final (04 → 06) + figuras (≈ 30 min)
python scripts/comparar_resultados.py            # o que mudou nos resultados em relação ao último commit
```

Os notebooks também podem ser abertos e executados um a um no Jupyter (kernel `vsr-st`), na ordem numérica. Cada
etapa lê as saídas das anteriores em `*/resultados_scripts/`, então é possível retomar de qualquer notebook.
Os backtests das etapas 41 e 42 ficam em cache (`previsoes_candidatos_ufs.csv`, `previsoes_lgbm_global.csv`);
apague esses arquivos para recalculá-los depois de alterar um modelo.

## Reprodutibilidade

A execução completa a partir dos microdados congelados reproduz os resultados versionados; os detalhes (ambiente,
o que é idêntico e o que varia com o otimizador numérico) estão em [`docs/REPRODUTIBILIDADE.md`](docs/REPRODUTIBILIDADE.md).

## Documentação

* `docs/RELATORIO_FINAL.md` — relatório do estudo (política V2; as etapas 41–43 estão descritas nos notebooks 04–06).
* `docs/NARRATIVA_DAS_DECISOES.md`, `docs/CONCLUSAO_EPIDEMIOLOGICA.md`, `docs/ENTENDIMENTO_TIPOS_MODELOS_IMPORTANTES_PARA_ESTUDO.md`,
  `docs/EXPLICACAO_INICIAL_ST.md` — narrativa, leitura epidemiológica e guias de apoio.
* `*/EXPLICACAO_DAS_DECISOES_*.md` — decisões de cada fase, com as figuras correspondentes.
