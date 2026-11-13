"""Caminhos do projeto e resumo do ambiente.

Os notebooks não usam mais caminhos relativos ("../../execucao_local_vsr"): tudo parte da raiz do repositório.

* ``DIR_EXECUCAO`` — dados brutos, intermediários e tratados (grandes, fora do git). Pode ser trocado pela variável
  de ambiente ``VSR_DIR_EXECUCAO``.
* ``pasta_etapa("etapa_27_...")`` — pasta versionada de resultados da etapa, dentro da fase a que ela pertence
  (etapas 1–11 tratamento, 12–19 análise exploratória, 20+ modelagem). É onde cada etapa grava e de onde as
  etapas seguintes leem.
"""
import os
import platform
import re
import sys
from pathlib import Path


def _relativo(caminho):
    """Relativo à pasta de trabalho (como nos notebooks originais), para não gravar caminhos da máquina nos resultados."""
    try:
        return Path(os.path.relpath(caminho))
    except ValueError:  # outra unidade de disco no Windows
        return caminho

RAIZ = _relativo(Path(__file__).resolve().parents[2])
DIR_EXECUCAO = Path(os.environ.get("VSR_DIR_EXECUCAO", RAIZ / "execucao_local_vsr"))

RESULTADOS = {
    "tratamento": RAIZ / "TRATAMENTO_DADOS_1_ETAPA" / "resultados_scripts",
    "analise": RAIZ / "ANALISE_EXPLORATORIA_2_ETAPA" / "resultados_scripts",
    "modelagem": RAIZ / "MODELAGEM_AVALIACAO_3_ETAPA" / "resultados_scripts",
}

def fase_da_etapa(numero):
    return "tratamento" if numero <= 11 else "analise" if numero <= 19 else "modelagem"

def pasta_etapa(nome):
    """Caminho versionado de uma etapa (ou de um arquivo/zip dela): 'etapa_25a_diagnostico_sarima' -> .../resultados_scripts/...

    Nomes sem prefixo 'etapa_N' são os arquivos avulsos das etapas 4–5, gravados na raiz dos resultados do tratamento.
    """
    numero = re.match(r"etapa_(\d+)", nome)
    fase = fase_da_etapa(int(numero.group(1))) if numero else "tratamento"
    return RESULTADOS[fase] / nome

def resumo_ambiente():
    """Imprime as versões que influenciam os resultados numéricos (ETS/SARIMA dependem do otimizador)."""
    import numpy, pandas, scipy, statsmodels  # noqa: E401  (import tardio: config não depende delas)

    print(f"Python: {sys.version.split()[0]} | {platform.platform()}")
    for modulo in (pandas, numpy, scipy, statsmodels):
        print(f"{modulo.__name__}: {modulo.__version__}")
    print(f"Raiz do repositório: {RAIZ}")
    print(f"Dados locais: {DIR_EXECUCAO}")
