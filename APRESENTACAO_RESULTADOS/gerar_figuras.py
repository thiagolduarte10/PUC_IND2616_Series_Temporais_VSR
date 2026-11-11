"""Gera as figuras da apresentação de resultados (Brasil, regiões e UFs).

Uso (a partir da raiz do repositório):
    python APRESENTACAO_RESULTADOS/gerar_figuras.py

Política final = etapa 43 (MinT-OAS não negativo sobre a Base V3 em h=1/4 e a Base V4 em h=8/13).
Referência "Base V2" = previsões-base independentes da etapa 37.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
MOD = RAIZ / "MODELAGEM_AVALIACAO_3_ETAPA" / "resultados_scripts"
OUT = Path(__file__).resolve().parent / "figuras"
OUT.mkdir(exist_ok=True)

HORIZ = [1, 4, 8, 13]
C_OBS, C_POL, C_BASE = "#1f2937", "#1264a3", "#f08c2e"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.3, "savefig.dpi": 200, "savefig.bbox": "tight"})

prev = pd.read_csv(MOD / "etapa_37_comparacao_final_hierarquica/previsoes_consolidadas_hierarquicas.csv",
                   parse_dates=["data_origem", "data_alvo"])
pol = pd.read_csv(MOD / "etapa_43_politica_final/previsoes_validacao_politica_final.csv",
                  parse_dates=["data_origem", "data_alvo"])
base = prev[prev.estrategia == "BASE_V2"]
intermit = (pd.read_csv(MOD / "etapa_29_referencias_ufs/metricas_por_uf_modelo_horizonte.csv")
            [["unidade", "regiao", "grupo_intermitencia", "percentual_semanas_zero"]].drop_duplicates("unidade"))


def mase(df):
    return df.groupby(["nivel", "unidade", "horizonte_semanas"]).mase_individual.mean()


m_pol, m_base = mase(pol), mase(base)

# Self-check: MASE médio por nível deve reproduzir a tabela oficial da etapa 43.
ref = pd.read_csv(MOD / "etapa_43_politica_final/metricas_politica_final.csv")
calc = pol.groupby(["nivel", "horizonte_semanas"]).mase_individual.mean()
for r in ref.itertuples():
    assert abs(calc[(r.nivel, r.horizonte_semanas)] - r.mase) < 1e-9, r

# Série semanal observada (somente semanas maduras), Brasil e regiões.
obs = pd.read_parquet(MOD / "etapa_20_preparacao_modelagem/painel_modelagem_brasil_regioes.parquet")
obs = (obs[obs.semana_madura & (obs.data >= "2021-12-01")]
       .rename(columns={"data": "data_alvo", "casos_vsr": "casos_observados"}))

# 1) Brasil: observado vs previsão da política por horizonte
fig, axes = plt.subplots(2, 2, figsize=(11, 5.6), sharex=True, sharey=True)
ob = obs[obs.unidade == "BRASIL"].sort_values("data_alvo")
for ax, h in zip(axes.flat, HORIZ):
    p = pol[(pol.unidade == "BRASIL") & (pol.horizonte_semanas == h)].sort_values("data_alvo")
    ax.plot(ob.data_alvo, ob.casos_observados, color=C_OBS, lw=1.2, label="Observado")
    ax.plot(p.data_alvo, p.previsao_final, "o-", color=C_POL, ms=3, lw=1, label="Política final")
    ax.set_title(f"h = {h} semana{'s' if h > 1 else ''}  (MASE {m_pol[('BRASIL', 'BRASIL', h)]:.2f})")
axes[0, 0].legend(frameon=False)
fig.supylabel("Internações/semana")
fig.savefig(OUT / "brasil_obs_vs_prev.png"); plt.close(fig)

# 2) MASE por nível e horizonte: Base V2 vs política
niveis = ["BRASIL", "REGIAO", "UF"]
mb = base.groupby(["nivel", "horizonte_semanas"]).mase_individual.mean()
fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
x = np.arange(len(HORIZ))
for ax, n in zip(axes, niveis):
    ax.bar(x - 0.2, [mb[(n, h)] for h in HORIZ], 0.4, color=C_BASE, label="Base V2 (independente)")
    ax.bar(x + 0.2, [calc[(n, h)] for h in HORIZ], 0.4, color=C_POL, label="Política final")
    ax.set_xticks(x, [f"h={h}" for h in HORIZ]); ax.set_title(n.title().replace("Regiao", "Regiões").replace("Uf", "UFs"))
axes[0].set_ylabel("MASE médio"); axes[0].legend(frameon=False, fontsize=8)
fig.savefig(OUT / "mase_nivel_horizonte.png"); plt.close(fig)


# 2b) Baselines (ingênuo e ingênuo sazonal) vs política final, por nível
nh = pd.read_csv(MOD / "etapa_26_comparacao_modelos_nao_hierarquicos/metricas_por_serie_modelo_horizonte.csv")
ufb = pd.read_csv(MOD / "etapa_29_referencias_ufs/metricas_por_uf_modelo_horizonte.csv").assign(nivel="UF")
bl = pd.concat([nh[nh.modelo.isin(["INGENUO", "INGENUO_SAZONAL"])], ufb])
bl = bl.groupby(["nivel", "modelo", "horizonte_semanas"]).mase.mean()
# Self-check: o ingênuo das UFs é a própria Base V2 em h=1 (mesma escala MASE da etapa 37).
assert abs(bl[("UF", "INGENUO", 1)] - mb[("UF", 1)]) < 1e-9
fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
for ax, n in zip(axes, niveis):
    ax.plot(HORIZ, [bl[(n, "INGENUO", h)] for h in HORIZ], "s--", color="#6b7280", label="Ingênuo")
    ax.plot(HORIZ, [bl[(n, "INGENUO_SAZONAL", h)] for h in HORIZ], "^--", color="#16a085", label="Ingênuo sazonal")
    ax.plot(HORIZ, [calc[(n, h)] for h in HORIZ], "o-", color=C_POL, lw=2, label="Política final")
    ax.set_xticks(HORIZ); ax.set_xlabel("Horizonte (semanas)")
    ax.set_title(n.title().replace("Regiao", "Regiões").replace("Uf", "UFs"))
axes[0].set_ylabel("MASE médio"); axes[0].legend(frameon=False, fontsize=8)
fig.savefig(OUT / "baselines_vs_politica.png"); plt.close(fig)
print(bl.unstack().round(3))

# 3) Heatmaps de MASE (regiões e UFs)
def heatmap(ax, mat, cmap, center=None, fmt="{:.2f}"):
    vmax = np.nanmax(np.abs(mat.values)) if center is not None else None
    im = ax.imshow(mat.values, cmap=cmap, aspect="auto",
                   vmin=-vmax if vmax else None, vmax=vmax)
    ax.set_xticks(range(mat.shape[1]), [f"h={h}" for h in mat.columns])
    ax.set_yticks(range(mat.shape[0]), mat.index)
    ax.grid(False)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, fmt.format(mat.values[i, j]), ha="center", va="center", fontsize=7)
    return im


reg_pol = m_pol["REGIAO"].unstack()
reg_delta = (m_pol["REGIAO"] - m_base["REGIAO"]).unstack()
for m in (reg_pol, reg_delta):
    m.index = [r.replace("_", "-").title() for r in m.index]
fig, axes = plt.subplots(1, 2, figsize=(11, 3.2), gridspec_kw={"wspace": 0.45})
plt.colorbar(heatmap(axes[0], reg_pol, "YlOrRd"), ax=axes[0]); axes[0].set_title("MASE da política final")
plt.colorbar(heatmap(axes[1], reg_delta, "RdBu_r", center=0, fmt="{:+.3f}"), ax=axes[1])
axes[1].set_title("Δ MASE (política − Base V2)")
fig.savefig(OUT / "regioes_mase.png"); plt.close(fig)

# 4) Regiões: observado vs previsão em h=4
regioes = sorted(m_pol["REGIAO"].index.get_level_values("unidade").unique())  # códigos, não rótulos
assert len(regioes) == 5
fig, axes = plt.subplots(len(regioes), 1, figsize=(10, 7), sharex=True)
for ax, r in zip(axes, regioes):
    o = obs[obs.unidade == r].sort_values("data_alvo")
    p = pol[(pol.unidade == r) & (pol.horizonte_semanas == 4)].sort_values("data_alvo")
    b = base[(base.unidade == r) & (base.horizonte_semanas == 4)].sort_values("data_alvo")
    ax.plot(o.data_alvo, o.casos_observados, color=C_OBS, lw=1)
    ax.plot(b.data_alvo, b.previsao_final, "s", color=C_BASE, ms=2.5)
    ax.plot(p.data_alvo, p.previsao_final, "o", color=C_POL, ms=2.5)
    assert len(o) and len(p) and len(b), r
    ax.set_ylabel(r.replace("_", "-").title(), fontsize=8, rotation=0, ha="right")
axes[0].legend(["Observado", "Base V2", "Política final"], frameon=False, ncol=3, fontsize=8, loc="upper left")
fig.savefig(OUT / "regioes_obs_vs_prev_h4.png"); plt.close(fig)

# 5) UFs: heatmap de MASE ordenado por intermitência
uf_pol = m_pol["UF"].unstack()
ordem = intermit.set_index("unidade").percentual_semanas_zero.sort_values()
uf_pol = uf_pol.loc[ordem.index]
uf_pol.index = [f"{u} ({ordem[u]:.0f}%)" for u in uf_pol.index]
fig, ax = plt.subplots(figsize=(5, 8))
plt.colorbar(heatmap(ax, uf_pol, "YlOrRd"), ax=ax, shrink=0.6)
ax.set_title("MASE da política por UF\n(% de semanas com zero casos)", fontsize=10)
fig.savefig(OUT / "ufs_mase_heatmap.png"); plt.close(fig)

# 6) UFs: ganho da política final sobre a Base V2 (h=1 e h=4)
d = (m_pol["UF"] - m_base["UF"]).unstack()[[1, 4]].loc[ordem.index]
fig, axes = plt.subplots(1, 2, figsize=(10, 6), sharey=True)
for ax, h in zip(axes, [1, 4]):
    v = d[h]
    ax.barh(v.index, v.values, color=np.where(v < 0, C_POL, C_BASE))
    ax.axvline(0, color="k", lw=0.8)
    ax.set_title(f"h={h}: {int((v < 0).sum())} de 27 UFs melhoram")
    ax.set_xlabel("Δ MASE (política − Base V2)")
axes[0].invert_yaxis()
fig.savefig(OUT / "ufs_delta_mint.png"); plt.close(fig)

# 7) UFs: MASE vs intermitência
u = uf_pol.copy(); u.index = ordem.index
grupo = intermit.set_index("unidade").grupo_intermitencia
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=False)
for ax, h in zip(axes, [1, 13]):
    for g, c in zip(sorted(grupo.unique()), ["#1264a3", "#f08c2e", "#c0392b", "#16a085"]):
        idx = grupo[grupo == g].index
        ax.scatter(ordem[idx], u.loc[idx, h], color=c, label=g.title().replace("_", " "), s=25)
    for k in ordem.index:
        ax.annotate(k, (ordem[k], u.loc[k, h]), fontsize=6, xytext=(2, 2), textcoords="offset points")
    ax.set_xlabel("% de semanas maduras com zero casos"); ax.set_title(f"h={h}")
axes[0].set_ylabel("MASE da política"); axes[0].legend(frameon=False, fontsize=8)
fig.savefig(OUT / "ufs_mase_vs_zeros.png"); plt.close(fig)

# 8) Previsão operacional do Brasil com faixas empíricas (etapa 43)
iv = pd.read_csv(MOD / "etapa_43_politica_final/intervalos_previsao_operacional.csv",
                 parse_dates=["data_alvo"])
iv = iv[iv.unidade == "BRASIL"].sort_values("data_alvo")
o = ob[ob.data_alvo >= "2024-07-01"]
fig, ax = plt.subplots(figsize=(10, 3.6))
ax.plot(o.data_alvo, o.casos_observados, color=C_OBS, lw=1.2, label="Observado (maduro)")
ax.fill_between(iv.data_alvo, iv.limite_inferior_95, iv.limite_superior_95, color=C_POL, alpha=0.15, label="Faixa 95%")
ax.fill_between(iv.data_alvo, iv.limite_inferior_80, iv.limite_superior_80, color=C_POL, alpha=0.3, label="Faixa 80%")
ax.plot(iv.data_alvo, iv.previsao_final, "o-", color=C_POL, label="Política final")
for r in iv.itertuples():
    ax.annotate(f"{r.previsao_final:.0f}", (r.data_alvo, r.previsao_final), xytext=(4, 4),
                textcoords="offset points", fontsize=8, color=C_POL)
ax.set_ylabel("Internações/semana"); ax.legend(frameon=False, fontsize=8, loc="upper left")
fig.savefig(OUT / "brasil_previsao_operacional.png"); plt.close(fig)

# Números usados nos slides
print("UFs que melhoram (h=1, h=4):", int((d[1] < 0).sum()), int((d[4] < 0).sum()))
print(reg_pol.round(3)); print(reg_delta.round(3))
print("Melhor/pior UF h=1:", uf_pol[1].idxmin(), uf_pol[1].min().round(3), uf_pol[1].idxmax(), uf_pol[1].max().round(3))
print("Correlação MASE h=1 x % zeros:", np.corrcoef(ordem, u[1])[0, 1].round(3))
