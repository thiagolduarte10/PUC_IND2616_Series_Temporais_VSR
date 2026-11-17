"""Painel de previsão de internações por VSR para planejamento de recursos (gestor público).

Lê apenas as saídas versionadas do pipeline (etapa 27: histórico da hierarquia; etapa 43: política final,
faixas de incerteza e validação) — não reajusta modelos. Para atualizar as previsões, reexecute o notebook 06.

    streamlit run dashboard/app.py        (a partir da raiz do repositório)
"""
import base64
import json
import math
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.colors import sample_colorscale
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
MODELAGEM = RAIZ / "MODELAGEM_AVALIACAO_3_ETAPA" / "resultados_scripts"
ETAPA_27 = MODELAGEM / "etapa_27_estrutura_hierarquica"
ETAPA_43 = MODELAGEM / "etapa_43_politica_final"
ASSETS = Path(__file__).parent / "assets"
LOGO = ASSETS / "logo_puc.png"  # opcional: se existir, aparece no cabeçalho

# Paleta PUC das apresentações do projeto (APRESENTACAO_RESULTADOS/*.tex)
NAVY, AZUL, CIANO, LARANJA, CINZA, CLARO = "#071B33", "#1264A3", "#32B4C8", "#F6A041", "#60708A", "#EEF4FA"
LARANJA_ESCURO = "#C96F12"  # previsão: mesmo matiz do laranja PUC, com contraste suficiente sobre branco
GRADE = "#DDE5EE"
FUNDO = "#F3F6FA"
FONTE = "Plus Jakarta Sans, Source Sans Pro, sans-serif"

HORIZONTES = [1, 4, 8, 13]
ANOS_PICO = [2022, 2023, 2024, 2025]  # temporadas completas pós-pandemia, referência do "pico típico"
REGIOES = {"NORTE": "Norte", "NORDESTE": "Nordeste", "CENTRO_OESTE": "Centro-Oeste", "SUDESTE": "Sudeste", "SUL": "Sul"}
UFS = {
    "AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá", "BA": "Bahia", "CE": "Ceará",
    "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MG": "Minas Gerais",
    "MS": "Mato Grosso do Sul", "MT": "Mato Grosso", "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco",
    "PI": "Piauí", "PR": "Paraná", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RO": "Rondônia",
    "RR": "Roraima", "RS": "Rio Grande do Sul", "SC": "Santa Catarina", "SE": "Sergipe", "SP": "São Paulo",
    "TO": "Tocantins",
}
# Código IBGE de cada UF, chave das feições em assets/br_ufs.geojson (malha do IBGE, qualidade mínima)
CODIGO_IBGE = {
    "RO": "11", "AC": "12", "AM": "13", "RR": "14", "PA": "15", "AP": "16", "TO": "17", "MA": "21", "PI": "22",
    "CE": "23", "RN": "24", "PB": "25", "PE": "26", "AL": "27", "SE": "28", "BA": "29", "MG": "31", "ES": "32",
    "RJ": "33", "SP": "35", "PR": "41", "SC": "42", "RS": "43", "MS": "50", "MT": "51", "GO": "52", "DF": "53",
}


def num(x, casas=0):
    """Número no padrão brasileiro (1.234,5)."""
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def nome_unidade(unidade):
    return "Brasil" if unidade == "BRASIL" else REGIOES.get(unidade) or UFS[unidade]


@st.cache_data
def carregar():
    painel = pd.read_parquet(ETAPA_27 / "painel_hierarquia_modelagem.parquet")
    previsoes = pd.read_csv(ETAPA_43 / "intervalos_previsao_operacional.csv", parse_dates=["data_origem", "data_alvo"])
    validacao = pd.read_csv(ETAPA_43 / "previsoes_validacao_politica_final.csv", parse_dates=["data_origem", "data_alvo"])
    quadros = {
        nome: pd.read_csv(ETAPA_43 / f"quadro_{nome}.csv")
        for nome in ("desempenho_politica_final", "cobertura_intervalos", "limitacoes_finais", "decisoes_por_horizonte")
    }
    picos = (
        painel[painel["ano_epi"].isin(ANOS_PICO)]
        .groupby(["unidade", "ano_epi"])["casos_vsr"].max()
        .groupby("unidade").median()
        .rename("pico_tipico")
    )
    previsoes = previsoes.merge(picos, on="unidade")
    # Unidades muito pequenas (pico típico < 1) não têm razão informativa: evita divisão por ~0
    previsoes["razao_pico"] = previsoes["previsao_final"] / previsoes["pico_tipico"].clip(lower=1)
    malha = json.loads((ASSETS / "br_ufs.geojson").read_text(encoding="utf-8"))
    return painel, previsoes, validacao, quadros, malha




def semanas_txt(h):
    return f"{h} semana{'s' if h > 1 else ''}"


def layout_base(fig, altura, titulo_y="Internações por semana"):
    fig.update_layout(
        height=altura, margin=dict(l=4, r=12, t=30, b=4), separators=",.",
        font=dict(family=FONTE, size=13, color=NAVY),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified",
        hoverlabel=dict(bgcolor="white", bordercolor=GRADE, font=dict(family=FONTE, color=NAVY)),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1, title=None, font=dict(color=CINZA)),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRADE, ticks="outside", tickcolor=GRADE, tickfont=dict(color=CINZA))
    fig.update_yaxes(title=dict(text=titulo_y, font=dict(color=CINZA, size=12)), gridcolor="#E9EEF5", zeroline=False,
                     rangemode="tozero", tickfont=dict(color=CINZA))
    return fig


def mostrar(fig):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def cabecalho_cartao(titulo, subtitulo=""):
    st.markdown(f'<div class="cartao-titulo">{titulo}</div><div class="cartao-sub">{subtitulo}</div>', unsafe_allow_html=True)


def grafico_previsao(historico, prev):
    """Histórico recente + previsões nos 4 horizontes, com faixas de 80% e 95%."""
    ultimo = historico.iloc[-1]
    # As faixas partem da última semana observada (largura zero) só para dar continuidade visual
    x = [ultimo["semana"]] + list(prev["data_alvo"])
    serie = lambda coluna: [ultimo["casos_vsr"]] + list(prev[coluna])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=historico["semana"], y=historico["casos_vsr"], mode="lines", name="Observado",
                             line=dict(color=AZUL, width=2.2), fill="tozeroy", fillcolor="rgba(18,100,163,0.08)",
                             hovertemplate="%{y:,.0f} internações<extra>Observado</extra>"))
    for nivel, opacidade in ((95, 0.16), (80, 0.30)):
        fig.add_trace(go.Scatter(x=x, y=serie(f"limite_superior_{nivel}"), mode="lines", line=dict(width=0),
                                 hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=x, y=serie(f"limite_inferior_{nivel}"), mode="lines", line=dict(width=0),
                                 fill="tonexty", fillcolor=f"rgba(246,160,65,{opacidade})", hoverinfo="skip",
                                 name=f"Faixa de {nivel}%"))
    fig.add_trace(go.Scatter(
        x=x, y=serie("previsao_final"), mode="lines+markers+text", name="Previsão",
        line=dict(color=LARANJA_ESCURO, width=2.2, dash="dot"),
        marker=dict(size=[0] + [11] * len(prev), color=LARANJA_ESCURO, line=dict(color="white", width=2)),
        text=[""] + [f"<b>{num(v)}</b>" for v in prev["previsao_final"]], textposition="top center",
        textfont=dict(color=NAVY, size=12),
        customdata=[[ultimo["casos_vsr"]] * 2] + prev[["limite_inferior_80", "limite_superior_80"]].values.tolist(),
        hovertemplate="%{y:,.0f} (80%: %{customdata[0]:,.0f} a %{customdata[1]:,.0f})<extra>Previsão</extra>",
    ))
    fig.add_vline(x=ultimo["semana"], line=dict(color=CINZA, width=1, dash="dash"))
    fig.add_annotation(x=ultimo["semana"], y=0.98, yref="paper", text="última semana observada ", showarrow=False,
                       xanchor="right", yanchor="top", font=dict(color=CINZA, size=11))
    return layout_base(fig, 420)


def grafico_sazonal(serie, prev):
    """Temporada atual contra as anteriores, por semana epidemiológica."""
    ano_atual = int(serie["ano_epi"].max())
    fig = go.Figure()
    for i, ano in enumerate(ANOS_PICO):
        s = serie[serie["ano_epi"] == ano]
        fig.add_trace(go.Scatter(x=s["semana_epi"], y=s["casos_vsr"], mode="lines", name="Temporadas 2022–2025",
                                 legendgroup="anteriores", showlegend=i == 0, line=dict(color="#B4BFCE", width=1.5),
                                 hovertemplate="%{y:,.0f}<extra>" + str(ano) + "</extra>"))
    atual = serie[serie["ano_epi"] == ano_atual]
    fig.add_trace(go.Scatter(x=atual["semana_epi"], y=atual["casos_vsr"], mode="lines", name=str(ano_atual),
                             line=dict(color=AZUL, width=3), hovertemplate="%{y:,.0f}<extra>" + str(ano_atual) + "</extra>"))
    semana_origem = int(atual["semana_epi"].iloc[-1])
    fig.add_trace(go.Scatter(x=semana_origem + prev["horizonte_semanas"], y=prev["previsao_final"], mode="markers",
                             name="Previsão", marker=dict(size=11, color=LARANJA_ESCURO, line=dict(color="white", width=2)),
                             hovertemplate="%{y:,.0f}<extra>Previsão</extra>"))
    layout_base(fig, 340)
    fig.update_xaxes(title=dict(text="Semana epidemiológica", font=dict(color=CINZA, size=12)), dtick=4, range=[1, 53])
    return fig


def contornos(malha):
    """Contorno (x, y), centro e área de cada UF, em projeção plana simples (longitude encolhida pela latitude média)."""
    sigla = {codigo: uf for uf, codigo in CODIGO_IBGE.items()}
    encolhe = math.cos(math.radians(15))
    saida = {}
    for feicao in malha["features"]:
        geometria = feicao["geometry"]
        poligonos = geometria["coordinates"] if geometria["type"] == "MultiPolygon" else [geometria["coordinates"]]
        aneis = sorted((p[0] for p in poligonos), key=len, reverse=True)  # só os anéis externos; o maior primeiro
        x, y = [], []
        for anel in aneis:
            x += [lon * encolhe for lon, _ in anel] + [None]
            y += [lat for _, lat in anel] + [None]
        xs, ys = [lon * encolhe for lon, _ in aneis[0]], [lat for _, lat in aneis[0]]
        saida[sigla[feicao["properties"]["codarea"]]] = dict(
            x=x, y=y, centro=((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2),
            area=(max(xs) - min(xs)) * (max(ys) - min(ys)))
    return saida


ESCALA_MAPA = [[0, "#E6EFF8"], [0.5, "#5B9BD0"], [1, "#0B3A66"]]


def grafico_mapa(prev_ufs, malha, selecao):
    """Mapa das UFs colorido pela previsão relativa ao pico típico de cada UF; `selecao` destaca a UF ou região escolhida."""
    formas = contornos(malha)
    fig = go.Figure()
    rotulos = dict(x=[], y=[], text=[], cor=[])
    # Das maiores para as menores, para que o DF fique por cima de Goiás
    for _, r in sorted(prev_ufs.iterrows(), key=lambda par: -formas[par[1]["unidade"]]["area"]):
        forma, pct = formas[r["unidade"]], r["razao_pico"] * 100
        destacada = selecao in (r["unidade"], r["regiao"])
        fig.add_trace(go.Scatter(
            x=forma["x"], y=forma["y"], mode="lines", fill="toself", hoveron="fills", hoverinfo="text", showlegend=False,
            fillcolor=sample_colorscale(ESCALA_MAPA, min(pct, 100) / 100)[0],
            line=dict(color=LARANJA if destacada else "white", width=2.5 if destacada else 1),
            text=f"<b>{UFS[r['unidade']]}</b><br>{num(r['previsao_final'])} internações na semana<br>{num(pct)}% do pico típico",
        ))
        if forma["area"] > 15:  # estados pequenos ficam sem sigla para não embolar; o valor aparece ao passar o mouse
            rotulos["x"].append(forma["centro"][0])
            rotulos["y"].append(forma["centro"][1])
            rotulos["text"].append(f"<b>{r['unidade']}</b><br>{num(r['previsao_final'])}")
            rotulos["cor"].append("white" if pct > 45 else NAVY)
    fig.add_trace(go.Scatter(x=rotulos["x"], y=rotulos["y"], mode="text", text=rotulos["text"], hoverinfo="skip",
                             showlegend=False, textfont=dict(size=10, color=rotulos["cor"], family=FONTE)))
    # Traço invisível só para desenhar a barra de cores
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", hoverinfo="skip", showlegend=False, marker=dict(
        color=[0], cmin=0, cmax=100, colorscale=ESCALA_MAPA, showscale=True,
        colorbar=dict(title=dict(text="% do pico típico", side="top", font=dict(size=11, color=CINZA)), orientation="h",
                      thickness=8, len=0.6, x=0.5, xanchor="center", y=0, yanchor="top", outlinewidth=0,
                      tickvals=[0, 50, 100], ticktext=["0%", "50%", "100%+"], tickfont=dict(color=CINZA, size=11)))))
    fig.update_layout(height=500, margin=dict(l=0, r=0, t=0, b=46), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family=FONTE, size=12, color=NAVY), dragmode=False, hovermode="closest",
                      hoverlabel=dict(bgcolor="white", bordercolor=GRADE, font=dict(family=FONTE, color=NAVY)))
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True, scaleanchor="x", scaleratio=1)
    return fig


def grafico_regioes(regioes_h):
    regioes_h = regioes_h.sort_values("previsao_final")
    fig = go.Figure(go.Bar(
        x=regioes_h["previsao_final"], y=regioes_h["unidade"].map(REGIOES), orientation="h", marker_color=AZUL, width=0.5,
        error_x=dict(type="data", symmetric=False, color=NAVY, thickness=1.5, width=5,
                     array=regioes_h["limite_superior_80"] - regioes_h["previsao_final"],
                     arrayminus=regioes_h["previsao_final"] - regioes_h["limite_inferior_80"]),
        customdata=regioes_h[["limite_inferior_80", "limite_superior_80"]],
        hovertemplate="%{x:,.0f} internações (80%: %{customdata[0]:,.0f} a %{customdata[1]:,.0f})<extra></extra>",
    ))
    layout_base(fig, 250, titulo_y=None)
    fig.update_layout(hovermode="closest", margin=dict(t=4))
    fig.update_xaxes(showgrid=True, gridcolor="#E9EEF5", rangemode="tozero", ticks="", showline=False)
    fig.update_yaxes(showgrid=False, tickfont=dict(color=NAVY, size=13))
    return fig


def grafico_validacao(val):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=val["data_alvo"], y=val["casos_observados"], mode="lines", name="Observado",
                             line=dict(color=AZUL, width=2.2), fill="tozeroy", fillcolor="rgba(18,100,163,0.08)",
                             hovertemplate="%{y:,.0f}<extra>Observado</extra>"))
    fig.add_trace(go.Scatter(x=val["data_alvo"], y=val["previsao_final"], mode="lines+markers", name="Previsto",
                             line=dict(color=LARANJA_ESCURO, width=2, dash="dot"), marker=dict(size=6),
                             hovertemplate="%{y:,.0f}<extra>Previsto</extra>"))
    return layout_base(fig, 340)


def silhueta(valores, largura=640, altura=150):
    """Curva da série do Brasil como SVG, usada só como ilustração de fundo do cabeçalho."""
    maximo = max(valores)
    pontos = " ".join(f"{i * largura / (len(valores) - 1):.1f},{altura - v / maximo * (altura - 8):.1f}"
                      for i, v in enumerate(valores))
    return (f'<svg class="silhueta" viewBox="0 0 {largura} {altura}" preserveAspectRatio="none" aria-hidden="true">'
            f'<polygon points="0,{altura} {pontos} {largura},{altura}" fill="rgba(255,255,255,0.07)"/>'
            f'<polyline points="{pontos}" fill="none" stroke="{LARANJA}" stroke-opacity="0.55" stroke-width="1.5"/></svg>')


def cartao_previsao(r, ultimo_valor, escala, destaque):
    """Cartão de um horizonte: valor previsto, variação e régua com a faixa de 80%."""
    h = int(r["horizonte_semanas"])
    variacao = r["previsao_final"] - ultimo_valor
    pos = lambda v: f"{min(v / escala, 1) * 100:.1f}%"
    largura = f"{max((r['limite_superior_80'] - r['limite_inferior_80']) / escala * 100, 1.5):.1f}%"
    return (
        f'<div class="kpi{" destaque" if destaque else ""}">'
        f'<div class="kpi-topo"><span class="kpi-rotulo">Em {semanas_txt(h)}</span><span class="kpi-data">{r["data_alvo"]:%d/%m/%Y}</span></div>'
        f'<div class="kpi-valor">{num(r["previsao_final"])}</div><div class="kpi-unidade">internações na semana</div>'
        f'<div class="regua"><div class="regua-faixa" style="left:{pos(r["limite_inferior_80"])};width:{largura}"></div>'
        f'<div class="regua-ponto" style="left:{pos(r["previsao_final"])}"></div></div>'
        f'<div class="kpi-linha"><span>Faixa de 80%</span><b>{num(r["limite_inferior_80"])} – {num(r["limite_superior_80"])}</b></div>'
        f'<div class="kpi-linha"><span>Ante a última semana</span><b>{"▲ +" if variacao >= 0 else "▼ −"}{num(abs(variacao))}</b></div>'
        f'<div class="kpi-linha"><span>Do pico típico</span><b>{num(r["razao_pico"] * 100)}%</b></div></div>'
    )


def cartao_metrica(rotulo, valor, explicacao):
    return (f'<div class="kpi"><div class="kpi-topo"><span class="kpi-rotulo">{rotulo}</span></div>'
            f'<div class="kpi-valor">{valor}</div><div class="kpi-unidade">{explicacao}</div></div>')


# ---------------------------------------------------------------------------------------------------------------------
st.set_page_config(page_title="Previsão de internações por VSR | PUC-Rio", page_icon="🏥", layout="wide",
                   initial_sidebar_state="collapsed")
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, .stApp, .stApp p, .stApp label, .stApp button, .stApp input, .stApp h1, .stApp h2, .stApp h3, .stApp li
  {{font-family: 'Plus Jakarta Sans', 'Source Sans Pro', sans-serif;}}
.stApp {{background: {FUNDO};}}
.block-container {{padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1240px;}}
header[data-testid="stHeader"] {{background: transparent;}}
[data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"], #MainMenu, footer {{display: none;}}

.hero {{position: relative; overflow: hidden; border-radius: 20px; padding: 30px 34px 26px; margin-bottom: 20px;
  background: linear-gradient(115deg, {NAVY} 0%, #0B2F57 55%, {AZUL} 130%); box-shadow: 0 10px 30px rgba(7,27,51,.18);}}
.hero .silhueta {{position: absolute; right: 0; bottom: 0; width: 58%; height: 100%; pointer-events: none;}}
.hero > div {{position: relative;}}
.hero-topo {{display: flex; align-items: center; gap: 12px; margin-bottom: 14px;}}
.hero-topo img {{height: 44px;}}
.marca {{color: {NAVY}; background: {LARANJA}; font-weight: 800; font-size: .78rem; letter-spacing: .08em; padding: 4px 10px; border-radius: 6px;}}
.sobretitulo {{color: #C7D6E8; font-size: .78rem; font-weight: 600; letter-spacing: .1em; text-transform: uppercase;}}
.hero h1 {{color: white; font-size: 2.15rem; font-weight: 800; letter-spacing: -.02em; margin: 0 0 6px; padding: 0; line-height: 1.15;}}
.hero p {{color: #C7D6E8; margin: 0 0 18px; font-size: 1rem; max-width: 46rem;}}
.chips {{display: flex; flex-wrap: wrap; gap: 8px;}}
.chip {{color: #E6EEF8; background: rgba(255,255,255,.10); border: 1px solid rgba(255,255,255,.18); border-radius: 999px;
  padding: 4px 12px; font-size: .8rem; font-weight: 500;}}
.chip.aviso {{color: {NAVY}; background: {LARANJA}; border-color: {LARANJA}; font-weight: 700;}}

[class*="st-key-cartao"] {{background: white; border: 1px solid #E3E9F1; border-radius: 16px; padding: 20px 22px 14px;
  box-shadow: 0 1px 2px rgba(7,27,51,.04), 0 6px 18px rgba(7,27,51,.05);}}
.cartao-titulo {{color: {NAVY}; font-size: 1.08rem; font-weight: 700; letter-spacing: -.01em;}}
.cartao-sub {{color: {CINZA}; font-size: .86rem; margin-top: 2px;}}
.secao {{color: {NAVY}; font-size: 1.35rem; font-weight: 800; letter-spacing: -.02em; margin: 6px 0 2px;}}
.secao-sub {{color: {CINZA}; font-size: .92rem; margin-bottom: 12px;}}
.nota {{color: {CINZA}; font-size: .84rem; margin: 0;}}

.kpis {{display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin: 4px 0 6px;}}
@media (max-width: 900px) {{.kpis {{grid-template-columns: repeat(2, minmax(0, 1fr));}}}}
.kpi {{background: white; border: 1px solid #E3E9F1; border-radius: 16px; padding: 18px 20px;
  box-shadow: 0 1px 2px rgba(7,27,51,.04), 0 6px 18px rgba(7,27,51,.05);}}
.kpi-topo {{display: flex; justify-content: space-between; align-items: baseline; gap: 8px;}}
.kpi-rotulo {{color: {AZUL}; font-size: .78rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase;}}
.kpi-data {{color: {CINZA}; font-size: .8rem; font-variant-numeric: tabular-nums;}}
.kpi-valor {{color: {NAVY}; font-size: 2.6rem; font-weight: 800; letter-spacing: -.03em; line-height: 1.1; margin-top: 8px;
  font-variant-numeric: tabular-nums;}}
.kpi-unidade {{color: {CINZA}; font-size: .84rem;}}
.regua {{position: relative; height: 6px; border-radius: 3px; background: #E9EEF5; margin: 16px 0 14px;}}
.regua-faixa {{position: absolute; top: 0; height: 6px; border-radius: 3px; background: {LARANJA};}}
.regua-ponto {{position: absolute; top: -4px; width: 14px; height: 14px; margin-left: -7px; border-radius: 50%;
  background: {NAVY}; border: 2px solid white; box-sizing: border-box;}}
.kpi-linha {{display: flex; justify-content: space-between; gap: 8px; font-size: .84rem; color: {CINZA}; padding: 3px 0;}}
.kpi-linha b {{color: {NAVY}; font-weight: 700; font-variant-numeric: tabular-nums;}}
.kpi.destaque {{background: linear-gradient(160deg, {NAVY}, #0E3B6B); border-color: {NAVY};}}
.kpi.destaque .kpi-rotulo {{color: {LARANJA};}}
.kpi.destaque .kpi-valor, .kpi.destaque .kpi-linha b {{color: white;}}
.kpi.destaque .kpi-data, .kpi.destaque .kpi-unidade, .kpi.destaque .kpi-linha {{color: #B9C8DC;}}
.kpi.destaque .regua {{background: rgba(255,255,255,.16);}}
.kpi.destaque .regua-ponto {{background: white; border-color: {NAVY};}}

.stTabs [data-baseweb="tab-list"] {{gap: 6px; background: white; border: 1px solid #E3E9F1; border-radius: 999px;
  padding: 5px; width: fit-content; margin-bottom: 10px;}}
.stTabs [data-baseweb="tab"] {{height: 38px; border-radius: 999px; padding: 0 18px; background: transparent;}}
.stTabs [data-baseweb="tab"] p {{font-weight: 600; font-size: .92rem; color: {CINZA};}}
.stTabs [aria-selected="true"] {{background: {NAVY};}}
.stTabs [aria-selected="true"] p {{color: white;}}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{display: none;}}

.tabela {{width: 100%; border-collapse: collapse; margin: 12px 0 10px; font-variant-numeric: tabular-nums;}}
.tabela th {{color: {CINZA}; font-size: .78rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
  text-align: right; padding: 8px 10px; border-bottom: 1px solid {GRADE};}}
.tabela td {{color: {NAVY}; text-align: right; padding: 10px; border-bottom: 1px solid #EEF2F7; font-size: .95rem;}}
.tabela th:first-child, .tabela td:first-child {{text-align: left; font-weight: 700;}}
.tabela .bom {{background: {CLARO}; color: {AZUL}; font-weight: 700; border-radius: 6px; padding: 2px 8px;}}
.limitacoes {{margin: 10px 0 0; padding: 0; list-style: none;}}
.limitacoes li {{color: {CINZA}; font-size: .88rem; padding: 9px 0 9px 14px; border-left: 3px solid {LARANJA}; margin-bottom: 8px;}}
.limitacoes li b {{color: {NAVY};}}
.rodape {{color: {CINZA}; font-size: .8rem; text-align: center; margin-top: 28px;}}
</style>
""", unsafe_allow_html=True)

painel, previsoes, validacao, quadros, malha = carregar()
origem = previsoes["data_origem"].iloc[0]
vencida = date.today() > previsoes["data_alvo"].max().date()

# --- Cabeçalho ---------------------------------------------------------------------------------------------------------
logo = f'<img src="data:image/png;base64,{base64.b64encode(LOGO.read_bytes()).decode()}" alt="PUC-Rio">' if LOGO.exists() else ""
aviso = '<span class="chip aviso">Datas-alvo já passaram · última execução do pipeline</span>' if vencida else ""
st.markdown(
    f'<div class="hero">{silhueta(painel[painel["unidade"] == "BRASIL"].sort_values("semana")["casos_vsr"].tail(260).tolist())}'
    f'<div><div class="hero-topo">{logo}<span class="marca">PUC-RIO</span>'
    f'<span class="sobretitulo">Engenharia Industrial · IND2616 Séries Temporais</span></div>'
    f"<h1>Previsão de internações por VSR</h1>"
    f"<p>Internações semanais de crianças menores de 2 anos por vírus sincicial respiratório, para apoiar o "
    f"planejamento de recursos no Brasil, nas regiões e nas UFs.</p>"
    f'<div class="chips"><span class="chip">Previsão emitida em {origem:%d/%m/%Y}</span>'
    f'<span class="chip">Horizontes de 1, 4, 8 e 13 semanas</span>'
    f'<span class="chip">Fonte: SIVEP-Gripe / OpenDataSUS</span>{aviso}</div></div></div>',
    unsafe_allow_html=True,
)

# --- Território --------------------------------------------------------------------------------------------------------
col_nivel, col_unidade, _ = st.columns([3, 4, 5])
nivel = col_nivel.segmented_control("Território", ["Brasil", "Região", "UF"], default="Brasil") or "Brasil"
if nivel == "Brasil":
    unidade = "BRASIL"
elif nivel == "Região":
    unidade = col_unidade.selectbox("Região", list(REGIOES), format_func=REGIOES.get)
else:
    ordenadas = sorted(UFS, key=UFS.get)
    unidade = col_unidade.selectbox("Unidade da federação", ordenadas, index=ordenadas.index("RJ"),
                                    format_func=lambda uf: f"{UFS[uf]} ({uf})")

titulo_local = nome_unidade(unidade)
prev = previsoes[previsoes["unidade"] == unidade].sort_values("horizonte_semanas")
serie = painel[painel["unidade"] == unidade].sort_values("semana")
ultimo = serie.iloc[-1]

aba_geral, aba_onde, aba_confianca = st.tabs(["Visão geral", "Por UF e região", "Confiabilidade"])

# --- Visão geral -------------------------------------------------------------------------------------------------------
with aba_geral:
    st.markdown(
        f'<div class="secao">{titulo_local}</div><div class="secao-sub">Internações previstas por semana · última semana '
        f'observada ({ultimo["semana"]:%d/%m/%Y}): <b>{num(ultimo["casos_vsr"])}</b></div>', unsafe_allow_html=True)
    escala = max(prev["limite_superior_80"].max(), 1)
    st.markdown('<div class="kpis">' + "".join(
        cartao_previsao(r, ultimo["casos_vsr"], escala, destaque=i == 0) for i, (_, r) in enumerate(prev.iterrows())
    ) + "</div>", unsafe_allow_html=True)
    st.markdown(
        f'<p class="nota">A régua mostra a faixa de 80% (laranja) e a previsão (ponto) na mesma escala nos quatro cartões. '
        f'Pico típico de {titulo_local}: mediana dos picos semanais de 2022–2025, '
        f'<b>{num(prev["pico_tipico"].iloc[0])}</b> internações.</p>', unsafe_allow_html=True)

    with st.container(key="cartao_previsao"):
        col_titulo, col_janela = st.columns([7, 3])
        with col_titulo:
            cabecalho_cartao("Histórico e previsão", "O modelo prevê quatro horizontes; a linha pontilhada apenas liga esses pontos.")
        janela = col_janela.segmented_control("Histórico exibido", ["1 ano", "2 anos", "Tudo"], default="2 anos",
                                              label_visibility="collapsed") or "2 anos"
        mostrar(grafico_previsao(serie.tail({"1 ano": 52, "2 anos": 104, "Tudo": len(serie)}[janela]), prev))

    with st.container(key="cartao_sazonal"):
        cabecalho_cartao("Em que ponto da temporada estamos",
                         f"{int(serie['ano_epi'].max())} comparado às temporadas de 2022 a 2025, por semana epidemiológica.")
        mostrar(grafico_sazonal(serie, prev))

# --- Por UF e região ---------------------------------------------------------------------------------------------------
with aba_onde:
    col_titulo, col_h = st.columns([7, 5])
    col_titulo.markdown('<div class="secao">Onde a demanda se concentra</div>'
                        '<div class="secao-sub">Previsão para todas as UFs e regiões no horizonte escolhido.</div>',
                        unsafe_allow_html=True)
    h_mapa = col_h.segmented_control("Horizonte", HORIZONTES, default=1, format_func=semanas_txt, key="h_mapa") or 1
    no_horizonte = previsoes[previsoes["horizonte_semanas"] == h_mapa]
    ufs_h = no_horizonte[no_horizonte["nivel"] == "UF"]
    col_mapa, col_tabela = st.columns([5, 7], gap="medium")
    with col_mapa.container(key="cartao_mapa"):
        cabecalho_cartao("Previsão em relação ao pico típico",
                         "Número = internações previstas; cor = quanto isso representa do pico típico da UF.")
        mostrar(grafico_mapa(ufs_h, malha, unidade))
    with col_tabela.container(key="cartao_ufs"):
        cabecalho_cartao("Internações previstas por UF", f"Semana de {ufs_h['data_alvo'].iloc[0]:%d/%m/%Y}, com a faixa de 80%.")
        tabela = ufs_h.assign(UF=ufs_h["unidade"].map(UFS), Região=ufs_h["regiao"].map(REGIOES),
                              pct_pico=ufs_h["razao_pico"] * 100).sort_values("previsao_final", ascending=False)
        st.dataframe(
            tabela[["UF", "Região", "previsao_final", "limite_inferior_80", "limite_superior_80", "pct_pico"]],
            hide_index=True, width="stretch", height=478,
            column_config={
                "previsao_final": st.column_config.NumberColumn("Previsão", format="%.0f", help="Internações na semana-alvo"),
                "limite_inferior_80": st.column_config.NumberColumn("Mín. 80%", format="%.0f"),
                "limite_superior_80": st.column_config.NumberColumn("Máx. 80%", format="%.0f"),
                "pct_pico": st.column_config.ProgressColumn("% do pico típico", format="%.0f%%", min_value=0, max_value=100),
            })
    with st.container(key="cartao_regioes"):
        cabecalho_cartao("Internações previstas por região", "A barra de erro indica a faixa de 80%.")
        mostrar(grafico_regioes(no_horizonte[no_horizonte["nivel"] == "REGIAO"]))
    st.markdown('<p class="nota">Em UFs com poucos casos, o percentual do pico típico oscila muito de uma semana para outra.</p>',
                unsafe_allow_html=True)

    exportar = previsoes.assign(territorio=previsoes["unidade"].map(nome_unidade))
    colunas = ["nivel", "territorio", "regiao", "data_origem", "data_alvo", "horizonte_semanas", "previsao_final",
               "limite_inferior_80", "limite_superior_80", "limite_inferior_95", "limite_superior_95"]
    st.download_button(
        "Baixar previsões de todos os territórios (CSV)",
        exportar[colunas].round(1).to_csv(index=False, sep=";", decimal=",", date_format="%d/%m/%Y").encode("utf-8-sig"),
        file_name=f"previsoes_vsr_{origem:%Y%m%d}.csv", mime="text/csv", type="primary")

# --- Confiabilidade ----------------------------------------------------------------------------------------------------
with aba_confianca:
    col_titulo, col_h = st.columns([7, 5])
    col_titulo.markdown(f'<div class="secao">{titulo_local}: quanto confiar na previsão</div>'
                        '<div class="secao-sub">Desempenho da política final quando aplicada ao passado.</div>',
                        unsafe_allow_html=True)
    h_val = col_h.segmented_control("Horizonte", HORIZONTES, default=1, format_func=semanas_txt, key="h_val") or 1
    val = validacao[(validacao["unidade"] == unidade) & (validacao["horizonte_semanas"] == h_val)].sort_values("data_alvo")
    cob = prev[prev["horizonte_semanas"] == h_val].iloc[0]
    st.markdown('<div class="kpis">' + "".join([
        cartao_metrica("Erro absoluto médio", num(val["erro_absoluto"].mean(), 1), "internações por semana, em média"),
        cartao_metrica("Viés médio", num(val["erro"].mean(), 1).replace("-", "−"), "negativo = tende a subestimar"),
        cartao_metrica("MASE", num(val["mase_individual"].mean(), 2), "abaixo de 1 supera a referência sazonal"),
        cartao_metrica("Cobertura da faixa de 80%", f"{num(cob['cobertura_80_loo'])}%", "das avaliações dentro da faixa"),
    ]) + "</div>", unsafe_allow_html=True)

    with st.container(key="cartao_validacao"):
        cabecalho_cartao(
            f"Previsto e observado, {semanas_txt(h_val)} à frente",
            f"{len(val)} previsões feitas entre {val['data_origem'].min():%m/%Y} e {val['data_origem'].max():%m/%Y}, "
            "sempre só com os dados disponíveis na data de cada previsão.")
        mostrar(grafico_validacao(val))

    col_a, col_b = st.columns(2, gap="medium")
    with col_a.container(key="cartao_mase"):
        cabecalho_cartao("Erro relativo (MASE) por nível e horizonte", "Média das 58 origens de validação.")
        mase = quadros["desempenho_politica_final"].pivot(index="nivel", columns="horizonte_semanas", values="mase_politica_final")
        celula = lambda v: f'<span class="bom">{num(v, 2)}</span>' if v < 1 else num(v, 2)
        linhas = "".join(
            f"<tr><td>{rotulo}</td>" + "".join(f"<td>{celula(mase.loc[n, h])}</td>" for h in HORIZONTES) + "</tr>"
            for n, rotulo in (("BRASIL", "Brasil"), ("REGIAO", "Regiões"), ("UF", "UFs")))
        st.markdown(
            '<table class="tabela"><tr><th>Nível</th>' + "".join(f"<th>{semanas_txt(h)}</th>" for h in HORIZONTES)
            + f"</tr>{linhas}</table>"
            '<p class="nota">Em destaque, os casos em que a política erra menos do que repetir a mesma semana do ano '
            "anterior. A previsão é mais confiável no curto prazo e nos níveis agregados.</p>", unsafe_allow_html=True)
    with col_b.container(key="cartao_limitacoes"):
        cabecalho_cartao("Limitações", "Registradas no quadro final do estudo (etapa 43).")
        st.markdown('<ul class="limitacoes">' + "".join(
            f"<li><b>{r['tema']}.</b> {r['descricao']}</li>" for _, r in quadros["limitacoes_finais"].iterrows()
        ) + "</ul>", unsafe_allow_html=True)
    with st.expander("Modelos usados em cada horizonte"):
        st.dataframe(quadros["decisoes_por_horizonte"].rename(columns={
            "horizonte_semanas": "Horizonte (semanas)", "base": "Base", "BRASIL": "Brasil", "REGIAO": "Regiões", "UF": "UFs",
            "estrategia_adotada": "Estratégia", "justificativa": "Justificativa"}), hide_index=True, width="stretch")

st.markdown(
    '<div class="rodape">Trabalho da disciplina IND2616 Séries Temporais · PUC-Rio · Para atualizar as previsões, '
    "reexecute o notebook 06_Politica_Final.ipynb com dados novos.</div>", unsafe_allow_html=True)
