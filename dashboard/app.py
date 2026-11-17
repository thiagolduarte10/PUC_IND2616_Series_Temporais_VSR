"""Painel de previsão de internações por VSR para planejamento de recursos (gestor público).

Lê apenas as saídas versionadas do pipeline (etapa 27: histórico da hierarquia; etapa 43: política final,
faixas de incerteza e validação) — não reajusta modelos. Para atualizar as previsões, reexecute o notebook 06.

    streamlit run dashboard/app.py        (a partir da raiz do repositório)
"""
import base64
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
MODELAGEM = RAIZ / "MODELAGEM_AVALIACAO_3_ETAPA" / "resultados_scripts"
ETAPA_27 = MODELAGEM / "etapa_27_estrutura_hierarquica"
ETAPA_43 = MODELAGEM / "etapa_43_politica_final"
LOGO = Path(__file__).parent / "assets" / "logo_puc.png"  # opcional: se existir, aparece no cabeçalho

# Paleta PUC das apresentações do projeto (APRESENTACAO_RESULTADOS/*.tex)
NAVY, AZUL, CIANO, LARANJA, CINZA, CLARO = "#071B33", "#1264A3", "#32B4C8", "#F6A041", "#60708A", "#EEF4FA"
LARANJA_ESCURO = "#C96F12"  # previsão: mesmo matiz do laranja PUC, com contraste suficiente sobre branco
GRADE = "#DDE5EE"

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
# Mapa em grade: (coluna, linha) de cada UF, aproximando a posição geográfica
GRADE_UFS = {
    "RR": (1, 0), "AP": (3, 0),
    "AM": (1, 1), "PA": (2, 1), "MA": (3, 1), "CE": (4, 1), "RN": (5, 1),
    "AC": (0, 2), "RO": (1, 2), "TO": (2, 2), "PI": (3, 2), "PB": (4, 2), "PE": (5, 2),
    "MT": (1, 3), "GO": (2, 3), "BA": (3, 3), "AL": (4, 3), "SE": (5, 3),
    "MS": (1, 4), "DF": (2, 4), "MG": (3, 4), "ES": (4, 4),
    "SP": (2, 5), "RJ": (3, 5),
    "PR": (2, 6), "SC": (2, 7), "RS": (2, 8),
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
    return painel, previsoes, validacao, quadros


def layout_base(fig, altura, titulo_y="Internações por semana"):
    fig.update_layout(
        height=altura, margin=dict(l=8, r=8, t=8, b=8), separators=",.",
        font=dict(family="Source Sans Pro, sans-serif", size=13, color=NAVY),
        paper_bgcolor="white", plot_bgcolor="white", hovermode="x unified",
        hoverlabel=dict(bgcolor="white", bordercolor=GRADE, font=dict(color=NAVY)),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, title=None),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRADE, ticks="outside", tickcolor=GRADE, tickfont=dict(color=CINZA))
    fig.update_yaxes(title=dict(text=titulo_y, font=dict(color=CINZA)), gridcolor=GRADE, zeroline=False,
                     rangemode="tozero", tickfont=dict(color=CINZA))
    return fig


def mostrar(fig):
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def grafico_previsao(historico, prev):
    """Histórico recente + previsões nos 4 horizontes, com faixas de 80% e 95%."""
    ultimo = historico.iloc[-1]
    # As faixas partem da última semana observada (largura zero) só para dar continuidade visual
    x = [ultimo["semana"]] + list(prev["data_alvo"])
    serie = lambda coluna: [ultimo["casos_vsr"]] + list(prev[coluna])
    fig = go.Figure()
    for nivel, opacidade in ((95, 0.16), (80, 0.30)):
        fig.add_trace(go.Scatter(x=x, y=serie(f"limite_superior_{nivel}"), mode="lines", line=dict(width=0),
                                 hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=x, y=serie(f"limite_inferior_{nivel}"), mode="lines", line=dict(width=0),
                                 fill="tonexty", fillcolor=f"rgba(246,160,65,{opacidade})", hoverinfo="skip",
                                 name=f"Faixa de {nivel}%"))
    fig.add_trace(go.Scatter(x=historico["semana"], y=historico["casos_vsr"], mode="lines", name="Observado",
                             line=dict(color=AZUL, width=2), hovertemplate="%{y:,.0f} internações<extra>Observado</extra>"))
    fig.add_trace(go.Scatter(
        x=x, y=serie("previsao_final"), mode="lines+markers", name="Previsão",
        line=dict(color=LARANJA_ESCURO, width=2, dash="dot"),
        marker=dict(size=[0] + [10] * len(prev), color=LARANJA_ESCURO, line=dict(color="white", width=2)),
        customdata=[[ultimo["casos_vsr"]] * 2] + prev[["limite_inferior_80", "limite_superior_80"]].values.tolist(),
        hovertemplate="%{y:,.0f} (80%: %{customdata[0]:,.0f} a %{customdata[1]:,.0f})<extra>Previsão</extra>",
    ))
    fig.add_vline(x=ultimo["semana"], line=dict(color=CINZA, width=1, dash="dash"))
    fig.add_annotation(x=ultimo["semana"], y=1, yref="paper", text="última semana observada ", showarrow=False,
                       xanchor="right", yanchor="top", font=dict(color=CINZA, size=12))
    return layout_base(fig, 400)


def grafico_sazonal(serie, prev):
    """Temporada atual contra as anteriores, por semana epidemiológica."""
    ano_atual = int(serie["ano_epi"].max())
    fig = go.Figure()
    for i, ano in enumerate(ANOS_PICO):
        s = serie[serie["ano_epi"] == ano]
        fig.add_trace(go.Scatter(x=s["semana_epi"], y=s["casos_vsr"], mode="lines", name="Temporadas 2022–2025",
                                 legendgroup="anteriores", showlegend=i == 0, line=dict(color="#A9B4C4", width=1.5),
                                 hovertemplate="%{y:,.0f}<extra>" + str(ano) + "</extra>"))
    atual = serie[serie["ano_epi"] == ano_atual]
    fig.add_trace(go.Scatter(x=atual["semana_epi"], y=atual["casos_vsr"], mode="lines", name=str(ano_atual),
                             line=dict(color=AZUL, width=2.5), hovertemplate="%{y:,.0f}<extra>" + str(ano_atual) + "</extra>"))
    semana_origem = int(atual["semana_epi"].iloc[-1])
    fig.add_trace(go.Scatter(x=semana_origem + prev["horizonte_semanas"], y=prev["previsao_final"], mode="markers",
                             name="Previsão", marker=dict(size=10, color=LARANJA_ESCURO, line=dict(color="white", width=2)),
                             hovertemplate="%{y:,.0f}<extra>Previsão</extra>"))
    layout_base(fig, 320)
    fig.update_xaxes(title=dict(text="Semana epidemiológica", font=dict(color=CINZA)), dtick=4, range=[1, 53])
    return fig


def grafico_mapa(prev_ufs):
    """Mapa em grade das UFs, colorido pela previsão relativa ao pico típico de cada UF."""
    colunas, linhas = 6, 9
    z = [[None] * colunas for _ in range(linhas)]
    texto = [[""] * colunas for _ in range(linhas)]
    extra = [[["", 0, 0]] * colunas for _ in range(linhas)]
    for _, r in prev_ufs.iterrows():
        c, l = GRADE_UFS[r["unidade"]]
        z[l][c] = min(r["razao_pico"] * 100, 100)
        texto[l][c] = f"<b>{r['unidade']}</b><br>{num(r['previsao_final'])}"
        extra[l][c] = [UFS[r["unidade"]], r["previsao_final"], r["razao_pico"] * 100]
    fig = go.Figure(go.Heatmap(
        z=z, text=texto, customdata=extra, texttemplate="%{text}", xgap=4, ygap=4, hoverongaps=False,
        zmin=0, zmax=100, colorscale=[[0, "#E3EEF8"], [0.5, "#5B9BD0"], [1, "#0B3A66"]],
        colorbar=dict(title=dict(text="% do pico<br>típico da UF", font=dict(size=12, color=CINZA)), thickness=10,
                      len=0.6, ticksuffix="%", tickvals=[0, 50, 100], ticktext=["0", "50", "100+"], outlinewidth=0),
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]:,.0f} internações/semana"
                      "<br>%{customdata[2]:,.0f}% do pico típico<extra></extra>",
    ))
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=8, b=0), separators=",.", paper_bgcolor="white",
                      plot_bgcolor="white", font=dict(family="Source Sans Pro, sans-serif", size=12, color=NAVY))
    fig.update_xaxes(visible=False, constrain="domain")
    fig.update_yaxes(visible=False, autorange="reversed", scaleanchor="x")
    return fig


def grafico_validacao(val):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=val["data_alvo"], y=val["casos_observados"], mode="lines", name="Observado",
                             line=dict(color=AZUL, width=2), hovertemplate="%{y:,.0f}<extra>Observado</extra>"))
    fig.add_trace(go.Scatter(x=val["data_alvo"], y=val["previsao_final"], mode="lines+markers", name="Previsto",
                             line=dict(color=LARANJA_ESCURO, width=2, dash="dot"), marker=dict(size=5),
                             hovertemplate="%{y:,.0f}<extra>Previsto</extra>"))
    return layout_base(fig, 320)


# ---------------------------------------------------------------------------------------------------------------------
st.set_page_config(page_title="Previsão de internações por VSR | PUC-Rio", page_icon="🏥", layout="wide")
st.markdown(f"""
<style>
.block-container {{padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1280px;}}
header[data-testid="stHeader"] {{background: transparent;}}
section[data-testid="stSidebar"] {{border-right: 1px solid {GRADE};}}
.faixa-puc {{background: {NAVY}; border-radius: 12px; padding: 22px 28px; border-bottom: 4px solid {LARANJA};
  display: flex; align-items: center; gap: 22px; margin-bottom: 18px;}}
.faixa-puc img {{height: 64px;}}
.faixa-puc .sobretitulo {{color: {LARANJA}; font-size: 0.78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;}}
.faixa-puc h1 {{color: white; font-size: 1.75rem; font-weight: 700; margin: 2px 0 4px; padding: 0; line-height: 1.2;}}
.faixa-puc p {{color: #C7D3E3; margin: 0; font-size: 0.95rem;}}
.cartoes {{display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin: 6px 0 18px;}}
@media (max-width: 900px) {{.cartoes {{grid-template-columns: repeat(2, minmax(0, 1fr));}}}}
.cartao {{background: white; border: 1px solid {GRADE}; border-top: 4px solid {AZUL}; border-radius: 10px; padding: 14px 16px;}}
.cartao .rotulo {{color: {CINZA}; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: .05em;}}
.cartao .valor {{color: {NAVY}; font-size: 2.1rem; font-weight: 700; line-height: 1.15; font-variant-numeric: tabular-nums;}}
.cartao .valor small {{font-size: 0.85rem; font-weight: 400; color: {CINZA};}}
.cartao .detalhe {{color: {CINZA}; font-size: 0.85rem; margin: 2px 0 0;}}
.nota {{color: {CINZA}; font-size: 0.85rem;}}
h3 {{color: {NAVY}; font-size: 1.15rem !important; padding-bottom: 0.2rem !important;}}
.stTabs [data-baseweb="tab"] {{font-weight: 600;}}
</style>
""", unsafe_allow_html=True)

painel, previsoes, validacao, quadros = carregar()
origem = previsoes["data_origem"].iloc[0]

# --- Barra lateral: território -----------------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Território")
    nivel = st.radio("Nível", ["Brasil", "Região", "UF"], horizontal=True, label_visibility="collapsed")
    if nivel == "Brasil":
        unidade = "BRASIL"
    elif nivel == "Região":
        unidade = st.selectbox("Região", list(REGIOES), format_func=REGIOES.get)
    else:
        unidade = st.selectbox("Unidade da federação", sorted(UFS, key=UFS.get), index=sorted(UFS, key=UFS.get).index("RJ"),
                               format_func=lambda uf: f"{UFS[uf]} ({uf})")

titulo_local = nome_unidade(unidade)
prev = previsoes[previsoes["unidade"] == unidade].sort_values("horizonte_semanas")
serie = painel[painel["unidade"] == unidade].sort_values("semana")
ultimo = serie.iloc[-1]
# --- Cabeçalho ---------------------------------------------------------------------------------------------------------
logo = f'<img src="data:image/png;base64,{base64.b64encode(LOGO.read_bytes()).decode()}" alt="PUC-Rio">' if LOGO.exists() else ""
st.markdown(
    f'<div class="faixa-puc">{logo}<div><div class="sobretitulo">PUC-Rio · Engenharia Industrial · IND2616 Séries Temporais</div>'
    f"<h1>Previsão de internações por VSR</h1>"
    f"<p>Crianças menores de 2 anos · SRAG (SIVEP-Gripe/OpenDataSUS) · apoio ao planejamento de recursos</p></div></div>",
    unsafe_allow_html=True,
)
if date.today() > prev["data_alvo"].max().date():
    st.warning(
        f"**Previsões emitidas em {origem:%d/%m/%Y}**, com dados até essa semana. Todas as datas-alvo já passaram: "
        "o painel mostra a última execução do pipeline. Para previsões atuais, atualize os dados e reexecute o "
        "notebook `06_Politica_Final.ipynb`.", icon="⚠️")
else:
    st.caption(f"Previsões emitidas em {origem:%d/%m/%Y}, com dados até essa semana.")

aba_geral, aba_onde, aba_confianca = st.tabs(["Visão geral", "Por UF e região", "Confiabilidade"])

# --- Visão geral -------------------------------------------------------------------------------------------------------
with aba_geral:
    st.markdown(f"### {titulo_local}: internações semanais previstas")
    cartoes = ""
    for _, r in prev.iterrows():
        h = int(r["horizonte_semanas"])
        variacao = r["previsao_final"] - ultimo["casos_vsr"]
        cartoes += (
            f'<div class="cartao"><div class="rotulo">Em {h} semana{"s" if h > 1 else ""} · {r["data_alvo"]:%d/%m/%Y}</div>'
            f'<div class="valor">{num(r["previsao_final"])} <small>internações/semana</small></div>'
            f'<div class="detalhe">Faixa de 80%: {num(r["limite_inferior_80"])} a {num(r["limite_superior_80"])}<br>'
            f'{"+" if variacao >= 0 else "−"}{num(abs(variacao))} em relação à última semana<br>'
            f'{num(r["razao_pico"] * 100)}% do pico típico</div></div>'
        )
    st.markdown(f'<div class="cartoes">{cartoes}</div>', unsafe_allow_html=True)

    janela = st.radio("Histórico exibido", ["1 ano", "2 anos", "Tudo"], index=1, horizontal=True)
    semanas = {"1 ano": 52, "2 anos": 104, "Tudo": len(serie)}[janela]
    mostrar(grafico_previsao(serie.tail(semanas), prev))
    st.markdown(
        f'<p class="nota">Última semana observada ({ultimo["semana"]:%d/%m/%Y}): <b>{num(ultimo["casos_vsr"])}</b> internações. '
        f"O modelo prevê 4 horizontes (1, 4, 8 e 13 semanas); a linha pontilhada apenas liga esses pontos. "
        f'Pico típico de {titulo_local} = mediana dos picos semanais de 2022–2025: '
        f'<b>{num(prev["pico_tipico"].iloc[0])}</b> internações.</p>',
        unsafe_allow_html=True)

    st.markdown("### Em que ponto da temporada estamos")
    mostrar(grafico_sazonal(serie, prev))

# --- Por UF e região-----------------------------------------------------------------------------------------------------
with aba_onde:
    st.markdown("### Internações previstas por UF")
    h_mapa = st.radio("Horizonte", HORIZONTES, horizontal=True, key="h_mapa",
                      format_func=lambda h: f"{h} semana{'s' if h > 1 else ''}")
    no_horizonte = previsoes[previsoes["horizonte_semanas"] == h_mapa]
    ufs_h = no_horizonte[no_horizonte["nivel"] == "UF"]
    col_mapa, col_tabela = st.columns([5, 7], gap="large")
    with col_mapa:
        mostrar(grafico_mapa(ufs_h))
        st.markdown(
            '<p class="nota">Cada quadro é uma UF: número = internações previstas na semana; cor = quanto isso '
            "representa do pico típico da própria UF (2022–2025). Em UFs com poucos casos o percentual oscila muito.</p>",
            unsafe_allow_html=True)
    with col_tabela:
        tabela = ufs_h.assign(
            UF=ufs_h["unidade"].map(UFS), Região=ufs_h["regiao"].map(REGIOES),
            pct_pico=ufs_h["razao_pico"] * 100,
        ).sort_values("previsao_final", ascending=False)
        st.dataframe(
            tabela[["UF", "Região", "previsao_final", "limite_inferior_80", "limite_superior_80", "pct_pico"]],
            hide_index=True, width="stretch", height=520,
            column_config={
                "previsao_final": st.column_config.NumberColumn("Previsão", format="%.0f", help="Internações na semana-alvo"),
                "limite_inferior_80": st.column_config.NumberColumn("Limite inf. 80%", format="%.0f"),
                "limite_superior_80": st.column_config.NumberColumn("Limite sup. 80%", format="%.0f"),
                "pct_pico": st.column_config.ProgressColumn("% do pico típico", format="%.0f%%", min_value=0, max_value=100),
            })

    st.markdown("### Regiões")
    regioes_h = no_horizonte[no_horizonte["nivel"] == "REGIAO"].sort_values("previsao_final")
    fig = go.Figure(go.Bar(
        x=regioes_h["previsao_final"], y=regioes_h["unidade"].map(REGIOES), orientation="h", marker_color=AZUL, width=0.55,
        error_x=dict(type="data", symmetric=False, color=CINZA, thickness=1.5, width=5,
                     array=regioes_h["limite_superior_80"] - regioes_h["previsao_final"],
                     arrayminus=regioes_h["previsao_final"] - regioes_h["limite_inferior_80"]),
        customdata=regioes_h[["limite_inferior_80", "limite_superior_80"]],
        hovertemplate="%{x:,.0f} internações (80%: %{customdata[0]:,.0f} a %{customdata[1]:,.0f})<extra></extra>",
    ))
    layout_base(fig, 260, titulo_y=None)
    fig.update_layout(hovermode="closest")
    fig.update_xaxes(title=dict(text="Internações previstas na semana (barra de erro = faixa de 80%)", font=dict(color=CINZA)),
                     showgrid=True, gridcolor=GRADE, rangemode="tozero")
    fig.update_yaxes(showgrid=False, tickfont=dict(color=NAVY))
    mostrar(fig)

    exportar = previsoes.assign(territorio=previsoes["unidade"].map(nome_unidade))
    colunas = ["nivel", "territorio", "regiao", "data_origem", "data_alvo", "horizonte_semanas", "previsao_final",
               "limite_inferior_80", "limite_superior_80", "limite_inferior_95", "limite_superior_95"]
    st.download_button(
        "Baixar previsões de todos os territórios (CSV)",
        exportar[colunas].round(1).to_csv(index=False, sep=";", decimal=",", date_format="%d/%m/%Y").encode("utf-8-sig"),
        file_name=f"previsoes_vsr_{origem:%Y%m%d}.csv", mime="text/csv")

# --- Confiabilidade ----------------------------------------------------------------------------------------------------
with aba_confianca:
    st.markdown(f"### {titulo_local}: como a previsão se saiu no passado")
    h_val = st.radio("Horizonte", HORIZONTES, horizontal=True, key="h_val",
                     format_func=lambda h: f"{h} semana{'s' if h > 1 else ''}")
    val = validacao[(validacao["unidade"] == unidade) & (validacao["horizonte_semanas"] == h_val)].sort_values("data_alvo")
    cob = prev[prev["horizonte_semanas"] == h_val].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Erro absoluto médio", f"{num(val['erro_absoluto'].mean(), 1)} / semana",
              help="Diferença média, em internações por semana, entre o previsto e o observado.")
    c2.metric("Viés médio", f"{num(val['erro'].mean(), 1)}", help="Negativo = o modelo tende a subestimar a demanda.")
    c3.metric("MASE", num(val["mase_individual"].mean(), 2),
              help="Abaixo de 1: erra menos do que repetir o valor da mesma semana do ano anterior.")
    c4.metric("Cobertura da faixa de 80%", f"{num(cob['cobertura_80_loo'])}%",
              help="Percentual das avaliações em que o valor observado caiu dentro da faixa de 80%.")
    mostrar(grafico_validacao(val))
    st.markdown(
        f'<p class="nota">{len(val)} previsões feitas entre {val["data_origem"].min():%m/%Y} e '
        f'{val["data_origem"].max():%m/%Y}, sempre usando só os dados disponíveis até a data de cada previsão.</p>',
        unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown("### Erro relativo (MASE) por nível e horizonte")
        desempenho = quadros["desempenho_politica_final"].pivot(
            index="nivel", columns="horizonte_semanas", values="mase_politica_final").loc[["BRASIL", "REGIAO", "UF"]]
        desempenho.index = ["Brasil", "Regiões", "UFs"]
        desempenho.columns = [f"{h} sem." for h in desempenho.columns]
        st.dataframe(desempenho.style.format(lambda v: num(v, 2)), width="stretch")
        st.markdown(
            '<p class="nota">Abaixo de 1, a política supera a referência sazonal. A previsão é mais confiável no '
            "curto prazo e nos níveis agregados; para UFs e horizontes de 8–13 semanas, use-a como tendência e "
            "planeje pela faixa, não pelo ponto.</p>", unsafe_allow_html=True)
    with col_b:
        st.markdown("### Limitações")
        for _, r in quadros["limitacoes_finais"].iterrows():
            st.markdown(f"- **{r['tema']}.** {r['descricao']}")
    with st.expander("Modelos usados em cada horizonte"):
        st.dataframe(quadros["decisoes_por_horizonte"], hide_index=True, width="stretch")
