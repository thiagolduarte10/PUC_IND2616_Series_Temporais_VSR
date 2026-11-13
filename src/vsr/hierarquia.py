"""Previsão hierárquica das etapas 41–43 (política final): hierarquia, métricas, MinT e LightGBM.

Concentra o que antes era copiado entre notebooks: hierarquia (S, ordem dos nós), painel semanal,
métricas com a escala MASE da etapa 37, MinT-OAS não negativo (transcrição das etapas 35/36) e os dois
LightGBM diretos (só UFs e global com os 33 nós).
"""
from functools import cache

import lightgbm as lgb
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

from vsr.config import RESULTADOS

RES = RESULTADOS["modelagem"]
DIR_27 = RES / "etapa_27_estrutura_hierarquica"

HORIZONTES = [1, 4, 8, 13]
H_MAX = max(HORIZONTES)
SEMANA = pd.Timedelta(days=7)
ORDEM_NIVEL = ["BRASIL", "REGIAO", "UF"]
COLUNAS = ["nivel", "unidade", "data_origem", "horizonte_semanas", "data_alvo", "casos_observados", "previsao"]
CHAVE = ["nivel", "unidade", "data_origem", "horizonte_semanas"]


def ler(caminho_relativo):
    """Lê um CSV de resultados_scripts convertendo as colunas de data conhecidas."""
    df = pd.read_csv(RES / caminho_relativo)
    for coluna in ("data_origem", "data_alvo", "data_inicio_treino"):
        if coluna in df.columns:
            df[coluna] = pd.to_datetime(df[coluna])
    return df


# --- Hierarquia: 33 nós (Brasil, 5 regiões, 27 UFs) e matriz S 33 x 27 ---
ESTRUTURA = pd.read_csv(DIR_27 / "estrutura_nos_hierarquia.csv").sort_values("ordem_no").reset_index(drop=True)
ORDEM_NOS = (ESTRUTURA["nivel"] + "_" + ESTRUTURA["unidade"]).tolist()
REGIAO_DO_NO = dict(zip(ORDEM_NOS, ESTRUTURA["regiao"]))
_matriz_s = pd.read_csv(DIR_27 / "matriz_somatoria_hierarquia.csv")
_matriz_s.index = _matriz_s["nivel"] + "_" + _matriz_s["unidade"]
_matriz_s = _matriz_s.reindex(ORDEM_NOS)
UFS_S = [c for c in _matriz_s.columns if c not in ("nivel", "unidade")]
S = _matriz_s[UFS_S].to_numpy(dtype=float)
assert S.shape == (33, 27) and np.linalg.matrix_rank(S) == 27

# --- Painel semanal maduro: todos os nós (Y) e só UFs com código da UF nas colunas (Y_UF) ---
PAINEL = pd.read_parquet(DIR_27 / "painel_hierarquia_modelagem.parquet")
assert PAINEL["semana_madura_13s"].all()
Y = (PAINEL.assign(no=PAINEL["nivel"] + "_" + PAINEL["unidade"])
     .pivot(index="semana", columns="no", values="casos_vsr").sort_index()[ORDEM_NOS])
Y.index.name, Y.columns.name = "ds", "unique_id"
assert Y.shape == (395, 33) and Y.notna().all().all()
assert np.allclose(Y.to_numpy(), Y[[f"UF_{u}" for u in UFS_S]].to_numpy() @ S.T)  # hierarquia histórica fecha
Y_UF = Y[[f"UF_{u}" for u in sorted(UFS_S)]].rename(columns=lambda no: no[3:])
Y_UF.columns.name = "unique_id"
EPI = PAINEL[PAINEL["nivel"] == "BRASIL"].set_index("semana")["semana_epi"].sort_index()


def anexar_observado(df):
    """Acrescenta casos_observados (NaN quando o alvo está além do painel, como na previsão operacional)."""
    no = df["nivel"] + "_" + df["unidade"]
    chave = pd.MultiIndex.from_arrays([df["data_alvo"], no])
    return df.assign(casos_observados=Y.stack().reindex(chave).to_numpy())


# --- Métricas (escala MASE sazonal por nó e origem, a mesma da etapa 37) ---
@cache
def escalas_mase():
    politica = ler("etapa_37_comparacao_final_hierarquica/previsoes_politica_hierarquica_proposta.csv")
    return politica.drop_duplicates(["nivel", "unidade", "data_origem"])[
        ["nivel", "unidade", "data_origem", "escala_mase_sazonal"]]


def com_erros(previsoes, coluna_prev="previsao"):
    """Linha a linha: escala MASE, erro, erro absoluto, erro quadrático e MASE individual."""
    base = previsoes.drop(columns="escala_mase_sazonal", errors="ignore").merge(
        escalas_mase(), on=["nivel", "unidade", "data_origem"], how="left")
    assert base["escala_mase_sazonal"].notna().all()
    erro = base[coluna_prev] - base["casos_observados"]
    return base.assign(erro=erro, erro_absoluto=erro.abs(), erro_quadratico=erro ** 2,
                       mase_individual=erro.abs() / base["escala_mase_sazonal"])


def metricas(previsoes, chaves, coluna_prev="previsao"):
    """MAE, RMSE, MASE sazonal e viés médio agregados por `chaves`."""
    base = com_erros(previsoes, coluna_prev)
    resultado = base.groupby(chaves).agg(avaliacoes=("erro", "size"), mae=("erro_absoluto", "mean"),
                                         rmse=("erro_quadratico", "mean"), mase=("mase_individual", "mean"),
                                         vies=("erro", "mean"))
    resultado["rmse"] = np.sqrt(resultado["rmse"])
    return resultado.reset_index()


# --- MinT-OAS não negativo (transcrição fiel das etapas 35/36) ---
def para_largo(base, coluna="previsao"):
    largo = base.assign(no=base["nivel"] + "_" + base["unidade"]).pivot_table(
        index=["data_origem", "horizonte_semanas"], columns="no", values=coluna)
    return largo[ORDEM_NOS]


def vetores_erro(base):
    """Erros de calibração (previsão − observado) em formato largo, na ordem dos nós."""
    return para_largo(base.assign(previsao=base["previsao"] - base["casos_observados"]))


def matrizes_mint(erros):
    """Piso do desvio no p10, padronização, encolhimento OAS, W = D·Σ·D, G = (SᵀW⁻¹S)⁻¹SᵀW⁻¹."""
    n, m = erros.shape
    desvios = erros.std(axis=0, ddof=1)
    piso = float(np.quantile(desvios[desvios > 1e-12], 0.10))
    desvios = np.maximum(desvios, piso)
    z = erros / desvios
    z = z - z.mean(axis=0, keepdims=True)
    cov = z.T @ z / n
    media_diag = float(np.trace(cov) / m)
    media_quad = float(np.mean(cov ** 2))
    denominador = (n + 1) * (media_quad - media_diag ** 2 / m)
    rho = 1.0 if denominador <= 1e-15 else float(np.clip((media_quad + media_diag ** 2) / denominador, 0, 1))
    W = np.diag(desvios) @ ((1 - rho) * cov + rho * media_diag * np.eye(m)) @ np.diag(desvios)
    W = (W + W.T) / 2
    assert np.linalg.eigvalsh(W).min() > 0
    W_inv = np.linalg.inv(W)
    G = np.linalg.solve(S.T @ W_inv @ S, S.T @ W_inv)
    assert np.abs(S @ G @ S - S).max() < 1e-8
    A = np.linalg.cholesky(W_inv).T @ S  # não negatividade: mínimos quadrados na métrica de W⁻¹
    return G, A, rho, piso


def reconciliar(largo_base, erros_calib):
    """largo_base: (data_origem, horizonte) x 33 nós. Devolve o mesmo formato reconciliado + diagnóstico."""
    saida, diagnostico = [], []
    for h in sorted(largo_base.index.get_level_values("horizonte_semanas").unique()):
        G, A, rho, piso = matrizes_mint(erros_calib.xs(h, level="horizonte_semanas").to_numpy(dtype=float))
        for chave, vetor in largo_base.xs(h, level="horizonte_semanas", drop_level=False).iterrows():
            folhas = G @ vetor.to_numpy(dtype=float)
            ativa = folhas.min() < -1e-8
            if ativa:
                resultado = lsq_linear(A, A @ folhas, bounds=(0.0, np.inf), method="trf", tol=1e-10, max_iter=2000)
                assert resultado.success
                folhas = resultado.x
            saida.append(pd.Series(S @ np.maximum(folhas, 0.0), index=ORDEM_NOS, name=chave))
            diagnostico.append({"data_origem": chave[0], "horizonte_semanas": h, "shrinkage_oas": rho,
                                "piso_desvio_erro": piso, "restricao_ativa": ativa})
    reconciliado = pd.DataFrame(saida)
    reconciliado.index = pd.MultiIndex.from_tuples(reconciliado.index, names=["data_origem", "horizonte_semanas"])
    reconciliado.columns.name = "no"
    assert np.allclose(reconciliado.to_numpy(), reconciliado[[f"UF_{u}" for u in UFS_S]].to_numpy() @ S.T)
    assert (reconciliado.to_numpy() >= -1e-9).all()
    return reconciliado, pd.DataFrame(diagnostico)


def reconciliar_longo(base, erros_calib):
    """Versão em formato longo (COLUNAS) para os backtests."""
    reconciliado, diagnostico = reconciliar(para_largo(base), erros_calib)
    longo = reconciliado.stack().rename("previsao").reset_index()
    longo[["nivel", "unidade"]] = longo["no"].str.split("_", n=1, expand=True)
    longo = longo.drop(columns="no").merge(base.drop(columns="previsao"), on=CHAVE)
    return longo[COLUNAS], diagnostico


# --- LightGBM direto (um modelo por horizonte), perda Tweedie ---
PARAMS_LGBM = dict(objective="tweedie", tweedie_variance_power=1.3, n_estimators=300, learning_rate=0.03,
                   num_leaves=15, min_child_samples=20, subsample=0.8, subsample_freq=1,
                   colsample_bytree=0.8, random_state=42, verbose=-1)
_ESCALONADAS = ["lag0", "lag1", "lag2", "lag3", "sazonal_52", "media4", "media8", "alvo"]
ATRIBUTOS_UF = ["lag0", "lag1", "lag2", "lag3", "sazonal_52", "media4", "media8", "zeros8", "semana_ano_alvo", "uf"]
ATRIBUTOS_GLOBAL = ["lag0", "lag1", "lag2", "lag3", "sazonal_52", "media4", "media8", "zeros8",
                    "semana_ano_alvo", "no", "nivel"]


def _tabela(matriz, h):
    """Linha (t, série): atributos com informação até t e alvo y[t+h]."""
    atributos = {f"lag{k}": matriz.shift(k) for k in range(4)}
    atributos["sazonal_52"] = matriz.shift(52 - h)  # y[t+h-52]: mesma semana do ano anterior ao alvo
    atributos["media4"] = matriz.rolling(4).mean()
    atributos["media8"] = matriz.rolling(8).mean()
    atributos["zeros8"] = (matriz == 0).astype(float).rolling(8).mean()
    atributos["alvo"] = matriz.shift(-h)
    tabela = pd.concat({nome: df.stack() for nome, df in atributos.items()}, axis=1).reset_index()
    tabela["semana_ano_alvo"] = ((tabela["ds"] + h * SEMANA).dt.dayofyear - 1) // 7 + 1
    return tabela


@cache
def _tabela_uf(h):
    tabela = _tabela(Y_UF, h)
    tabela["uf"] = pd.Categorical(tabela["unique_id"], categories=list(Y_UF.columns))
    return tabela


@cache
def _tabela_global(h):
    tabela = _tabela(Y, h)
    tabela["no"] = pd.Categorical(tabela["unique_id"], categories=ORDEM_NOS)
    tabela["nivel"] = pd.Categorical(tabela["unique_id"].str.split("_").str[0], categories=ORDEM_NIVEL)
    return tabela


def _ajustar_prever(tabela, origem, h, atributos, ids):
    treino = tabela[(tabela["ds"] + h * SEMANA <= origem) & tabela["alvo"].notna()]
    assert (treino["ds"] + h * SEMANA).max() <= origem  # sem vazamento
    modelo = lgb.LGBMRegressor(**PARAMS_LGBM).fit(treino[atributos], treino["alvo"])
    teste = tabela[tabela["ds"] == origem].set_index("unique_id").reindex(ids)
    return modelo.predict(teste[atributos])


def _saida(nivel, unidade, origem, h, previsao):
    return pd.DataFrame({"nivel": nivel, "unidade": unidade, "data_origem": origem, "horizonte_semanas": h,
                         "data_alvo": origem + h * SEMANA, "previsao": np.clip(previsao, 0.0, None)})


def prever_lgbm_uf(origem, horizontes=HORIZONTES):
    """LightGBM global sobre as 27 UFs (escala original). Etapa 41: LGBM_TWEEDIE."""
    ids = list(Y_UF.columns)
    return pd.concat([_saida("UF", ids, origem, h, _ajustar_prever(_tabela_uf(h), origem, h, ATRIBUTOS_UF, ids))
                      for h in horizontes], ignore_index=True)


def prever_lgbm_global(origem, horizontes=HORIZONTES):
    """LightGBM global sobre os 33 nós, normalizados pela média de treino do nó. Etapa 42: LGBM_GLOBAL."""
    # shortcut: escala = média do treino (piso 0,1); trocar por média das últimas 52 semanas se houver deriva de nível
    escala = Y.loc[:origem].mean().clip(lower=0.1)
    partes = []
    for h in horizontes:
        tabela = _tabela_global(h).copy()
        tabela[_ESCALONADAS] = tabela[_ESCALONADAS].div(tabela["unique_id"].map(escala).to_numpy(), axis=0)
        previsao = _ajustar_prever(tabela, origem, h, ATRIBUTOS_GLOBAL, ORDEM_NOS) * escala[ORDEM_NOS].to_numpy()
        nivel, unidade = zip(*(no.split("_", 1) for no in ORDEM_NOS))
        partes.append(_saida(list(nivel), list(unidade), origem, h, previsao))
    return pd.concat(partes, ignore_index=True)


# --- Candidatos e composição das bases ---
def origens():
    """(origens de calibração do MinT, origens formais de validação)."""
    calib = ler("etapa_34_calibracao_temporal_mint/previsoes_calibracao_mint.csv")["data_origem"].unique()
    formais = ler("etapa_27_estrutura_hierarquica/calendario_validacao_hierarquica.csv")["data_origem"].unique()
    calib, formais = sorted(calib), sorted(formais)
    assert len(calib) == 39 and len(formais) == 58 and max(calib) < min(formais)
    return calib, formais


def carregar_candidatos():
    """{modelo: {"FORMAL"|"CALIBRACAO": previsões longas}} para BASE_V2 e os LightGBM das etapas 41/42."""
    calib, formais = origens()
    base_v2 = ler("etapa_30_previsoes_base_hierarquicas_v2/previsoes_base_hierarquicas_v2.csv")
    calib_v2 = ler("etapa_34_calibracao_temporal_mint/previsoes_calibracao_mint.csv")
    uf_41 = ler("etapa_41_modelos_intermitentes_ufs/previsoes_candidatos_ufs.csv")
    uf_41 = uf_41.loc[uf_41["modelo"] == "LGBM_TWEEDIE"].assign(nivel="UF")
    global_42 = ler("etapa_42_lgbm_global_vs_ets/previsoes_lgbm_global.csv")
    return {
        "BASE_V2": {"FORMAL": base_v2[COLUNAS], "CALIBRACAO": calib_v2[COLUNAS]},
        "LGBM_TWEEDIE_UF": {"FORMAL": uf_41.loc[uf_41["data_origem"].isin(formais), COLUNAS],
                            "CALIBRACAO": uf_41.loc[uf_41["data_origem"].isin(calib), COLUNAS]},
        "LGBM_GLOBAL": {"FORMAL": global_42.loc[global_42["data_origem"].isin(formais), COLUNAS],
                        "CALIBRACAO": global_42.loc[global_42["data_origem"].isin(calib), COLUNAS]},
    }


def compor_base(candidatos, escolha, periodo):
    """escolha: {(nivel, horizonte): modelo}. Monta a base com 33 nós x horizontes."""
    partes = []
    for (nivel, h), modelo in escolha.items():
        df = candidatos[modelo][periodo]
        partes.append(df[(df["nivel"] == nivel) & (df["horizonte_semanas"] == h)].assign(modelo_base=modelo))
    return pd.concat(partes, ignore_index=True)
