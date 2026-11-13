"""Compara os CSVs de resultados da cópia de trabalho com os de uma referência do git (verificação de reprodutibilidade).

    python scripts/comparar_resultados.py                 # contra HEAD
    python scripts/comparar_resultados.py --ref main --saida comparacao.csv

Para cada CSV em */resultados_scripts: IGUAL (diferença relativa ≤ --tol em todas as colunas numéricas e textos
idênticos), DIFERENTE (com a pior diferença por coluna), FORMATO_DIFERENTE, NOVO ou AUSENTE. Colunas de data/hora de
execução e caminhos locais são ignoradas.
"""
import argparse
import io
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
VOLATEIS = ("data_download", "momento", "caminho", "data_execucao", "gerado_em", "tempo_", "duracao")


def git(*args):
    return subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True, check=True).stdout


def comparar(a, b, tol):
    volateis = [c for c in a.columns if any(v in c.lower() for v in VOLATEIS)]
    a, b = a.drop(columns=volateis), b.drop(columns=volateis, errors="ignore")
    if a.shape != b.shape or list(a.columns) != list(b.columns):
        return "FORMATO_DIFERENTE", f"{a.shape} vs {b.shape}"
    piores = []
    for coluna in a.columns:
        x, y = a[coluna], b[coluna]
        if pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y):
            x, y = x.to_numpy(float), y.to_numpy(float)
            relativa = np.abs(x - y) / np.maximum(np.abs(x), 1.0)
            relativa = np.where(np.isnan(x) & np.isnan(y), 0.0, relativa)
            pior = np.nanmax(relativa) if len(relativa) else 0.0
            if np.isnan(relativa).any() or pior > tol:
                piores.append(f"{coluna}: rel {pior:.1e} ({(relativa > tol).sum()} linhas)")
        else:
            diferentes = (x.fillna("<NA>").astype(str) != y.fillna("<NA>").astype(str)).sum()
            if diferentes:
                piores.append(f"{coluna}: {diferentes} textos")
    return ("IGUAL", "") if not piores else ("DIFERENTE", "; ".join(piores))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--tol", type=float, default=1e-6)
    parser.add_argument("--saida", help="grava a tabela completa neste CSV")
    args = parser.parse_args()

    na_ref = {p for p in git("ls-tree", "-r", "--name-only", args.ref).decode().splitlines()
              if "/resultados_scripts/" in p and p.endswith(".csv")}
    na_copia = {p.relative_to(RAIZ).as_posix() for p in RAIZ.glob("*/resultados_scripts/**/*.csv")}

    linhas = []
    for caminho in sorted(na_ref | na_copia):
        if caminho not in na_copia:
            status, detalhe = "AUSENTE", ""
        elif caminho not in na_ref:
            status, detalhe = "NOVO", ""
        else:
            ref = pd.read_csv(io.BytesIO(git("show", f"{args.ref}:{caminho}")), low_memory=False)
            status, detalhe = comparar(ref, pd.read_csv(RAIZ / caminho, low_memory=False), args.tol)
        linhas.append({"etapa": caminho.split("/")[2] if caminho.count("/") > 2 else "(raiz)",
                       "arquivo": caminho, "status": status, "detalhe": detalhe})

    tabela = pd.DataFrame(linhas)
    if args.saida:
        tabela.to_csv(args.saida, index=False)
    print(tabela["status"].value_counts().to_string(), "\n")
    resumo = tabela.groupby("etapa", sort=False)["status"].agg(lambda s: f"{(s == 'IGUAL').sum()}/{len(s)} iguais")
    print(resumo.to_string(), "\n")
    with pd.option_context("display.max_colwidth", 140, "display.width", 250):
        print(tabela.loc[tabela["status"] != "IGUAL", ["arquivo", "status", "detalhe"]].to_string(index=False))


if __name__ == "__main__":
    main()
