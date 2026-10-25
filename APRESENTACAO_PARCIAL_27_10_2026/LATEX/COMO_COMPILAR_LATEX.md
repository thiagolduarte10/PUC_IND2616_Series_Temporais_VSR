# Como compilar a apresentação LaTeX Beamer

## Arquivos da apresentação

- `APRESENTACAO_PARCIAL_PROFESSOR_BEAMER.tex`: fonte da apresentação.
- `figuras/`: gráficos usados pelos slides.

Mantenha o arquivo `.tex` e a pasta `figuras` juntos. O PDF será gerado na mesma pasta.

## Instalação recomendada no Windows

Recomendo instalar o **TeX Live** para Windows, na modalidade completa. Ele inclui `pdflatex`, Beamer e os pacotes usados nesta apresentação.

1. Baixe o instalador oficial `install-tl-windows.exe` em [TeX Live para Windows](https://tug.org/texlive/windows.html).
2. Execute o instalador e mantenha uma instalação completa para evitar instalação manual de pacotes durante a compilação.
3. Depois de concluir, feche e abra novamente o PowerShell ou o VS Code.
4. Confirme a instalação com:

```powershell
pdflatex --version
```

O TeX Live adiciona os executáveis ao `PATH` automaticamente. A documentação oficial recomenda evitar diretórios de instalação com caracteres não ASCII. Para o projeto, uma pasta simples como `C:\latex-vsr` é uma alternativa segura se a compilação via caminho WSL apresentar problema.

## Compilação pelo PowerShell

Abra o PowerShell na pasta `LATEX` e execute duas vezes:

```powershell
pdflatex -interaction=nonstopmode APRESENTACAO_PARCIAL_PROFESSOR_BEAMER.tex
pdflatex -interaction=nonstopmode APRESENTACAO_PARCIAL_PROFESSOR_BEAMER.tex
```

O arquivo final será `APRESENTACAO_PARCIAL_PROFESSOR_BEAMER.pdf`.

Executar duas vezes atualiza corretamente o total de slides no rodapé. Se ocorrer erro de permissão usando `\\wsl.localhost`, copie a pasta `LATEX` inteira para uma pasta local sem espaços nem acentos, por exemplo `C:\latex-vsr`, e execute os mesmos comandos nela.

## Compilação pelo VS Code

Opcionalmente, instale a extensão **LaTeX Workshop** no VS Code. Abra o arquivo `.tex` e use o comando `LaTeX Workshop: Build LaTeX project`. A extensão apenas facilita a compilação e a visualização; o TeX Live continua sendo necessário.

## Ajustes rápidos

- Para alterar texto, edite apenas o arquivo `.tex`.
- Para substituir um gráfico, mantenha o mesmo nome dentro de `figuras/` ou atualize o comando `\includegraphics` correspondente.
- Não envie somente o `.tex` para outra pessoa: envie a pasta `LATEX` inteira ou um arquivo `.zip` dela.
