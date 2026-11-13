"""Obtenção reprodutível dos microdados SRAG (SIVEP-Gripe / OpenDataSUS) — etapas 2 a 3.

O estudo usa versões fixas dos arquivos Parquet publicados pelo Ministério da Saúde (``ARQUIVOS_OFICIAIS_SRAG``).
Cada arquivo baixado tem o SHA-256 registrado em ``manifesto_download_srag.csv``; numa nova execução, uma cópia local
cujo hash confere com o manifesto é reutilizada sem acessar a rede (dados congelados).
"""
import hashlib
import os
import re
from datetime import datetime, timezone

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PORTAL_OPENDATASUS = "https://opendatasus.saude.gov.br"
PACKAGE_ID_SRAG = "39a4995f-4a6e-440f-8c8f-b00c81fae0d0"
S3_OFICIAL = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br"

# Versões congeladas usadas no estudo (2019–2024 publicadas em 23/03/2026; 2025–2026 em 19/10/2026).
ARQUIVOS_OFICIAIS_SRAG = {
    2019: f"{S3_OFICIAL}/SRAG/2019/INFLUD19-23-03-2026.parquet",
    2020: f"{S3_OFICIAL}/SRAG/2020/INFLUD20-23-03-2026.parquet",
    2021: f"{S3_OFICIAL}/SRAG/2021/INFLUD21-23-03-2026.parquet",
    2022: f"{S3_OFICIAL}/SRAG/2022/INFLUD22-23-03-2026.parquet",
    2023: f"{S3_OFICIAL}/SRAG/2023/INFLUD23-23-03-2026.parquet",
    2024: f"{S3_OFICIAL}/SRAG/2024/INFLUD24-23-03-2026.parquet",
    2025: f"{S3_OFICIAL}/SRAG/2025/INFLUD25-19-10-2026.parquet",
    2026: f"{S3_OFICIAL}/SRAG/2026/INFLUD26-19-10-2026.parquet",
}


def sessao_http():
    """Sessão com novas tentativas para erros transitórios do servidor."""
    sessao = requests.Session()
    tentativas = Retry(total=4, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
                       allowed_methods=["GET", "HEAD"])
    sessao.mount("https://", HTTPAdapter(max_retries=tentativas))
    return sessao


def consultar_catalogo():
    """Etapa 2: recursos do pacote SRAG na API CKAN do OpenDataSUS.

    A API passou a responder HTML em vez de JSON; nesse caso o catálogo fica indisponível (None) e o estudo segue
    com as versões fixadas em ``ARQUIVOS_OFICIAIS_SRAG`` — o catálogo é só documentação, não entrada do pipeline.
    """
    url = f"{PORTAL_OPENDATASUS}/api/3/action/package_show?id={PACKAGE_ID_SRAG}"
    try:
        resposta = sessao_http().get(url, timeout=60)
        resposta.raise_for_status()
        catalogo = resposta.json()
        if not catalogo.get("success"):
            raise ValueError("a API não retornou sucesso")
    except (requests.RequestException, ValueError) as erro:
        print(f"Catálogo do OpenDataSUS indisponível ({type(erro).__name__}: {str(erro)[:120]}).")
        print("Seguindo com as versões fixadas em vsr.dados_srag.ARQUIVOS_OFICIAIS_SRAG.")
        return None, None
    pacote = catalogo["result"]
    recursos = pd.DataFrame(pacote["resources"])
    colunas = [c for c in ["name", "format", "url", "created", "last_modified", "description"] if c in recursos]
    recursos = recursos[colunas].sort_values("name", kind="stable").reset_index(drop=True)
    manifesto = {
        "fonte": pacote.get("title"),
        "url_catalogo": f"{PORTAL_OPENDATASUS}/dataset/{pacote.get('name', '')}",
        "momento_consulta_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "package_id": PACKAGE_ID_SRAG,
        "quantidade_recursos": len(recursos),
    }
    return manifesto, recursos


def data_publicacao_no_nome(url):
    resultado = re.search(r"INFLUD\d{2}-(\d{2})-(\d{2})-(\d{4})", url)
    if resultado is None:
        return None
    dia, mes, ano = resultado.groups()
    return datetime.strptime(f"{dia}-{mes}-{ano}", "%d-%m-%Y").date()


def verificar_arquivo(url):
    """Etapa 2B: existência, tamanho, data de modificação e ETag no servidor (HEAD)."""
    try:
        resposta = sessao_http().head(url, allow_redirects=True, timeout=(20, 90))
        return {
            "status_http": resposta.status_code,
            "acessivel": resposta.ok,
            "tamanho_mb": round(int(resposta.headers.get("Content-Length", 0)) / 1024**2, 2),
            "modificado_no_servidor": resposta.headers.get("Last-Modified"),
            "etag": resposta.headers.get("ETag"),
            "erro": None,
        }
    except requests.RequestException as erro:
        return {"status_http": None, "acessivel": False, "tamanho_mb": None,
                "modificado_no_servidor": None, "etag": None, "erro": str(erro)}


def manifesto_arquivos_oficiais():
    """Etapa 2B: uma linha por ano com a URL fixada e o resultado da verificação."""
    return pd.DataFrame([
        {"ano": ano, "arquivo": url.split("/")[-1], "data_publicacao_no_nome": data_publicacao_no_nome(url),
         "url_oficial": url, **verificar_arquivo(url)}
        for ano, url in ARQUIVOS_OFICIAIS_SRAG.items()
    ])


def calcular_sha256(caminho, tamanho_bloco=1024 * 1024):
    hash_arquivo = hashlib.sha256()
    with open(caminho, "rb") as arquivo:
        while bloco := arquivo.read(tamanho_bloco):
            hash_arquivo.update(bloco)
    return hash_arquivo.hexdigest()


def hashes_congelados(arquivo_manifesto):
    """{arquivo: sha256} do manifesto de uma execução anterior (vazio se não existir)."""
    if not arquivo_manifesto.exists():
        return {}
    return pd.read_csv(arquivo_manifesto).set_index("arquivo")["sha256"].to_dict()


def arquivo_congelado(destino, hashes):
    return destino.name in hashes and destino.exists() and calcular_sha256(destino) == hashes[destino.name]


def baixar_arquivo_srag(ano, url, destino, hashes=None):
    """Etapa 3: usa a cópia congelada (hash confere) ou baixa por streaming, conferindo tamanho e SHA-256."""
    from tqdm.auto import tqdm

    hashes = hashes or {}
    if arquivo_congelado(destino, hashes):
        tamanho = destino.stat().st_size
        return {"origem": "arquivo_congelado_local", "bytes_baixados": tamanho, "bytes_esperados": tamanho,
                "sha256": hashes[destino.name]}

    sessao = sessao_http()
    destino.parent.mkdir(parents=True, exist_ok=True)
    resposta_head = sessao.head(url, allow_redirects=True, timeout=(20, 90))
    resposta_head.raise_for_status()
    tamanho_esperado = int(resposta_head.headers.get("Content-Length", 0))

    if destino.exists() and destino.stat().st_size == tamanho_esperado:
        return {"origem": "arquivo_já_existente", "bytes_baixados": destino.stat().st_size,
                "bytes_esperados": tamanho_esperado, "sha256": calcular_sha256(destino)}

    temporario = destino.with_suffix(destino.suffix + ".part")
    resposta = sessao.get(url, stream=True, timeout=(20, 300))
    resposta.raise_for_status()
    hash_arquivo, bytes_baixados = hashlib.sha256(), 0
    with open(temporario, "wb") as arquivo, tqdm(total=tamanho_esperado, unit="B", unit_scale=True,
                                                desc=f"Baixando {ano}") as barra:
        for bloco in resposta.iter_content(chunk_size=1024 * 1024):
            arquivo.write(bloco)
            hash_arquivo.update(bloco)
            bytes_baixados += len(bloco)
            barra.update(len(bloco))
    if tamanho_esperado and bytes_baixados != tamanho_esperado:
        raise IOError(f"Download incompleto em {ano}: {bytes_baixados} de {tamanho_esperado} bytes.")
    sha256 = hash_arquivo.hexdigest()
    if destino.name in hashes and sha256 != hashes[destino.name]:
        os.remove(temporario)
        raise IOError(f"{destino.name}: o arquivo publicado mudou (SHA-256 diferente do manifesto congelado).")
    os.replace(temporario, destino)
    return {"origem": "download_nesta_execucao", "bytes_baixados": bytes_baixados,
            "bytes_esperados": tamanho_esperado, "sha256": sha256}
