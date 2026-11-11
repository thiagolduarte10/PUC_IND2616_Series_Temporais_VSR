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

MASE médio nas 58 origens de validação (dez/2021 – abr/2026), política anterior (V2) → final:

| Nível | h=1 | h=4 | h=8 | h=13 |
|---|---|---|---|---|
| Brasil | 0,332 → **0,288** | 1,202 → **0,802** | 1,575 → **1,541** | 1,522 → **1,457** |
| Regiões | 0,534 → **0,480** | 1,417 → **1,113** | 1,775 → **1,700** | **1,883** → 1,889 |
| UFs | 1,133 → **1,077** | 2,211 → **1,918** | 2,990 → **2,745** | 3,122 → **3,056** |

Quadros completos: `MODELAGEM_AVALIACAO_3_ETAPA/resultados_scripts/etapa_43_politica_final/`.

## Estrutura

```
TRATAMENTO_DADOS_1_ETAPA/         etapas 1–11  download, limpeza, painel semanal, atraso e maturidade (13 semanas)
ANALISE_EXPLORATORIA_2_ETAPA/     etapas 12–19 sazonalidade, intermitência das UFs, autocorrelação, calendário de validação
MODELAGEM_AVALIACAO_3_ETAPA/
  notebook_parcial_modelagem_avaliacao/  etapas 20–40 referências, ETS, SARIMA(X), hierarquia, bottom-up, top-down,
                                         MinT; política V2 (37–40 ficam como registro histórico)
  notebook_politica_final/               etapas 41–43 (política final)
    vsr_hier.py                          funções compartilhadas: hierarquia, métricas, MinT, LightGBM
    Etapa_41_Modelos_Intermitentes_UFs   Croston/SBA/TSB/ADIDA/IMAPA, GLM binomial negativo, LightGBM nas UFs
    Etapa_42_LGBM_Global_vs_ETS          LightGBM global (33 nós) vs ETS nos agregados
    Etapa_43_Politica_Final              validação, previsão operacional, plausibilidade, faixas, quadros finais
  resultados_scripts/etapa_XX_*/         saídas (CSV/PNG) de cada etapa
APRESENTACAO_RESULTADOS/          slides de resultados e gerar_figuras.py
APRESENTACAO_PARCIAL_27_10_2026/  apresentação parcial
*.md (raiz)                       relatório final, narrativa das decisões, conclusão epidemiológica, guia de modelos
```

Cada pasta de etapa tem um `EXPLICACAO_DAS_DECISOES_*.md` com as justificativas.

## Como executar

```bash
conda create -n vsr-intermit python=3.12 -y
conda activate vsr-intermit
pip install -r requirements.txt
python -m ipykernel install --user --name vsr-intermit
```

* **Etapas 41–43 e figuras** — usam só os arquivos versionados em `resultados_scripts/`:
  ```bash
  cd MODELAGEM_AVALIACAO_3_ETAPA/notebook_politica_final
  jupyter nbconvert --to notebook --execute --inplace Etapa_41_Modelos_Intermitentes_UFs.ipynb  # ~2 min
  jupyter nbconvert --to notebook --execute --inplace Etapa_42_LGBM_Global_vs_ETS.ipynb        # ~2 min
  jupyter nbconvert --to notebook --execute --inplace Etapa_43_Politica_Final.ipynb
  cd ../.. && python APRESENTACAO_RESULTADOS/gerar_figuras.py
  ```
  Os backtests das etapas 41 e 42 ficam em cache (`previsoes_candidatos_ufs.csv`, `previsoes_lgbm_global.csv`);
  apague esses arquivos para recalcular depois de alterar um modelo.
* **Etapas 1–40** — precisam dos dados brutos/intermediários: extraia `execucao_local_vsr.zip` na raiz do repositório
  (cria `execucao_local_vsr/`, ignorada pelo git). Os notebooks leem `../../execucao_local_vsr` a partir da própria pasta
  e gravam as saídas em `execucao_local_vsr/saidas/`; as cópias versionadas estão em `resultados_scripts/`.
