# Reprodução e organização do projeto

Documento conferido contra os scripts da branch em 14/11/2026. Nesta revisão documental não foram reexecutados modelos.

## Caminhos e responsabilidades

`src/vsr/config.py` resolve a raiz e as pastas por fase. As saídas CSV/PNG ficam em `*/resultados_scripts/etapa_XX_*/`, dentro do repositório. Dados brutos, intermediários e tratados ficam em `DIR_EXECUCAO`.

O padrão é `<raiz_do_repositorio>/execucao_local_vsr`. Estar ignorada pelo Git não significa estar fisicamente fora do repositório. Para continuar com a pasta irmã usada anteriormente no WSL:

```bash
export VSR_DIR_EXECUCAO=/home/thiago/Series-Temporais-Trabalho/execucao_local_vsr
```

Defina essa variável antes de abrir o kernel ou executar o pipeline; um kernel já iniciado pode conservar configuração anterior.

## Ambiente

As dependências declaradas estão em `requirements.txt` e `environment.yml`; o pacote `vsr` é instalado em modo editável por `-e .`. Não basta copiar um notebook isolado, pois ele importa código de `src/vsr/`.

```bash
conda env create -f environment.yml
conda activate vsr-st
python -m ipykernel install --user --name vsr-st --display-name "Python 3.13 (vsr-st)"
```

São instruções declaradas pelo projeto; esta revisão não testou uma instalação limpa das dependências.

## Execução

Na raiz, com ambiente e caminhos configurados:

```bash
python scripts/executar_pipeline.py
python scripts/executar_pipeline.py --de 4 --ate 6
python scripts/executar_pipeline.py --de 3 --ate 3 --sem-figuras
```

Os números dos argumentos são números de notebook, não etapas 4, 6 ou 3. Cada notebook usa um kernel novo e depende de arquivos das fases anteriores. O executor grava saídas nos próprios notebooks, inclusive em execução interrompida, e pode alterar CSVs/figuras versionados.

## Fonte congelada e caches

O catálogo fixa URLs dos oito Parquet. Arquivos locais cujo hash confere com o manifesto podem ser reutilizados. Guarde manifesto e cópias originais juntos; não presuma identidade só por nome ou tamanho. A função de download também contém uma reutilização por tamanho: verifique os SHA-256 se houver suspeita de alteração da fonte.

As etapas 41/42 reutilizam arquivos de previsões existentes. Reexecução com cache não comprova novo treinamento. Se parâmetros, atributos, fonte ou ambiente mudarem, preserve uma cópia identificada dos resultados anteriores e planeje a regeneração dos caches antes de comparar. Não apague resultados só para ler os notebooks.

## Comparação de resultados

```bash
python scripts/comparar_resultados.py
python scripts/comparar_resultados.py --ref 8981194 --saida comparacao_reorganizacao.csv
```

O padrão compara com HEAD. Para medir o efeito do commit de reorganização, a referência anterior é 8981194. O script compara CSVs linha a linha, ignora algumas colunas voláteis e usa tolerância numérica. Não compara PDFs nem comprova equivalência metodológica dos notebooks.

O commit 4baa3b9 declara preservação dos rankings e pequenas diferenças de otimização. Essa declaração não deve ser apresentada como uma reexecução independente feita nesta revisão documental. Alterações em previsões e convergência exigem exame das auditorias, não apenas arredondamento das métricas.

## Limites da reprodutibilidade

Reproduzir resultados de uma fonte congelada não reconstrói as versões que estavam publicadas em cada semana histórica. O backtest atual usa registros consolidados; disponibilidade histórica e revisão das notificações continuam sendo limitações.

As etapas 37–40 são a primeira política; 43 é a vigente. PDFs e LaTeX não são recompilados automaticamente por esta edição documental. O executor gera figuras da apresentação, mas não contém uma etapa de compilação dos PDFs.
