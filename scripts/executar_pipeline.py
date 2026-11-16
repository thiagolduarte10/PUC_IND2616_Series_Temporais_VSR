"""Executa o pipeline completo (ou um trecho) na ordem, gravando as saídas nos próprios notebooks.

    python scripts/executar_pipeline.py              # 01 a 06 + figuras da apresentação
    python scripts/executar_pipeline.py --de 4       # só a política final (04 a 06) + figuras
    python scripts/executar_pipeline.py --de 3 --ate 3 --sem-figuras

Cada notebook roda num kernel novo, com a pasta do notebook como diretório de trabalho; o primeiro erro interrompe
a execução (o notebook é gravado até a célula que falhou, para diagnóstico). Tempos de referência (Windows, 1 CPU
por kernel): 01 ≈ 3 min, 02 ≈ 1 min, 03 ≈ 2 h 40 min (SARIMA da etapa 25 ≈ 2 h 20 min), 04–06 ≈ 30 min.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

RAIZ = Path(__file__).resolve().parents[1]
NOTEBOOKS = [
    RAIZ / "TRATAMENTO_DADOS_1_ETAPA" / "01_Tratamento_Dados.ipynb",
    RAIZ / "ANALISE_EXPLORATORIA_2_ETAPA" / "02_Analise_Exploratoria.ipynb",
    RAIZ / "MODELAGEM_AVALIACAO_3_ETAPA" / "03_Modelagem_Avaliacao.ipynb",
    RAIZ / "MODELAGEM_AVALIACAO_3_ETAPA" / "04_Modelos_Intermitentes_UFs.ipynb",
    RAIZ / "MODELAGEM_AVALIACAO_3_ETAPA" / "05_LGBM_Global_vs_ETS.ipynb",
    RAIZ / "MODELAGEM_AVALIACAO_3_ETAPA" / "06_Politica_Final.ipynb",
]


def gravar(notebook, caminho):
    """Grava o notebook trocando a pasta do usuário por ~ (avisos do kernel trazem caminhos temporários locais)."""
    casa = json.dumps(str(Path.home()))[1:-1]  # como aparece escapado no JSON
    caminho.write_text(nbformat.writes(notebook).replace(casa, "~") + "\n", encoding="utf-8")


def executar(caminho, kernel):
    notebook = nbformat.read(caminho, as_version=4)
    cliente = NotebookClient(notebook, timeout=6 * 3600, kernel_name=kernel,
                             resources={"metadata": {"path": str(caminho.parent)}})
    inicio = time.time()
    try:
        cliente.execute()
    finally:
        gravar(notebook, caminho)
        print(f"  {caminho.name}: {(time.time() - inicio) / 60:.1f} min", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--de", type=int, default=1, help="primeiro notebook (1–6)")
    parser.add_argument("--ate", type=int, default=len(NOTEBOOKS), help="último notebook (1–6)")
    parser.add_argument("--kernel", default="vsr-st", help="kernel Jupyter do ambiente do projeto")
    parser.add_argument("--sem-figuras", action="store_true", help="não regenerar as figuras da apresentação")
    args = parser.parse_args()

    for caminho in NOTEBOOKS[args.de - 1:args.ate]:
        print(f"{time.strftime('%H:%M:%S')} {caminho.relative_to(RAIZ)}", flush=True)
        try:
            executar(caminho, args.kernel)
        except CellExecutionError as erro:
            print(f"ERRO em {caminho.name}:\n{str(erro)[-3000:]}", file=sys.stderr)
            sys.exit(1)

    if not args.sem_figuras and args.ate == len(NOTEBOOKS):
        print(f"{time.strftime('%H:%M:%S')} APRESENTACAO_RESULTADOS/gerar_figuras.py", flush=True)
        subprocess.run([sys.executable, str(RAIZ / "APRESENTACAO_RESULTADOS" / "gerar_figuras.py")], check=True)
    print(f"{time.strftime('%H:%M:%S')} concluído", flush=True)


if __name__ == "__main__":
    main()
