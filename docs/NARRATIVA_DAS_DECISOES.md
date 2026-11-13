# Narrativa das decisões — da fonte bruta à política final de previsão

**Projeto:** Previsão hierárquica de internações por SRAG associada ao VSR em menores de dois anos  
**Disciplina:** IND2616 — Séries Temporais, PUC-Rio

## A história que o trabalho conta

Este projeto não começou pela escolha de um algoritmo. Começou com uma pergunta operacional: como antecipar, semana a semana, a demanda hospitalar associada ao VSR em crianças pequenas sem esconder as diferenças entre UFs, regiões e Brasil?

A resposta não poderia ser apenas “usar o modelo mais complexo”. Para que uma previsão tenha utilidade, ela precisa partir de uma base definida, respeitar o tempo em que a informação se torna disponível, ser comparada honestamente com alternativas simples e, neste caso, somar corretamente ao longo da geografia brasileira. As 40 etapas do estudo foram organizadas para tornar essa história verificável.

## 1. Antes de prever, foi necessário definir o que seria previsto

Os microdados do SIVEP-Gripe registram notificações de SRAG, não uma série pronta de VSR. Por isso, as primeiras etapas não ajustaram nenhum modelo. Elas responderam a perguntas básicas: qual versão dos arquivos será usada? Qual data representa o momento epidemiológico? O que significa uma confirmação por VSR? Como tratar várias versões da mesma notificação? Que local geográfico deve representar o caso?

A fonte escolhida foi o conjunto oficial de microdados SRAG 2019–2026 do OpenDataSUS. Os oito arquivos anuais foram congelados e verificados por URL, tamanho e hash. Essa escolha evita que o estudo se torne irreproduzível quando o portal atualizar um arquivo ou quando a API deixar de responder. O conjunto bruto tinha 4.678.812 notificações e 194 campos comuns a todos os anos.

O evento de interesse foi definido com precisão: criança de 0 a menos de 24 meses, hospitalizada, residente em uma UF válida, com início de sintomas válido e confirmação de VSR por PCR ou antígeno. A data de início de sintomas foi escolhida como relógio da série porque se aproxima do início epidemiológico do evento e está completa na fonte. Ausência de exame específico não foi transformada em resultado negativo, pois “não informado” não significa “VSR ausente”.

## 2. A limpeza não foi apenas remover linhas

O tratamento foi uma etapa de investigação. Todas as 194 colunas foram inventariadas antes de fixar as variáveis do estudo; isso evitou inferir significados apenas por siglas. Os códigos de idade foram convertidos para meses e os campos laboratoriais foram normalizados, para que valores como `1` e `1.0` não fossem tratados como resultados diferentes.

Houve um ponto importante de controle de qualidade: duas notificações apareciam duplicadas, em quatro linhas, com informações temporais conflitantes. A análise não decidiu simplesmente apagar tudo. Primeiro a execução foi interrompida; depois os grupos foram examinados e uma regra determinística foi definida: priorizar defasagem válida entre sintomas e notificação, menor defasagem, digitação mais recente e arquivo mais recente. Duas linhas foram removidas e a base final ficou com 158.358 notificações, sem duplicidades remanescentes.

Essa decisão é relevante porque uma duplicidade pode mudar a semana do evento. Em uma série semanal, deslocar casos entre semanas pode criar ou suavizar artificialmente um pico. Deduplicar de forma auditável foi mais importante do que simplesmente produzir uma base menor.

## 3. O dado observado ainda não era o dado disponível para previsão

Uma contagem recente pode parecer baixa apenas porque parte das notificações ou dos resultados laboratoriais ainda não chegou ao sistema. A etapa de atrasos mediu a data em que cada caso se tornou disponível. A mediana anual do atraso ficou entre 8 e 13 dias, e o maior percentil 95 anual alcançou 86 dias em 2021.

Daí veio a regra de maturidade: uma semana só poderia entrar em treino e avaliação se estivesse fechada e tivesse ao menos 13 semanas até a data de corte da fonte, 19/10/2026. A regra é deliberadamente conservadora. Ela não apaga as semanas recentes; apenas impede que elas sejam confundidas com observações finais.

O painel semanal resultante possui 407 semanas, de 30/12/2018 a 11/10/2026, para 27 UFs, cinco regiões e Brasil. As 395 semanas até 19/07/2026 são maduras. Esse foi um avanço metodológico central: a comparação passa a simular o que seria conhecido no momento da previsão, em vez de usar retrospectivamente um futuro ainda não consolidado.

## 4. A exploração mostrou que não existe uma única série brasileira

Os gráficos e estatísticas mostraram sazonalidade anual clara, mas não um calendário único e rígido. No Brasil, os picos ocorreram nas semanas epidemiológicas 11 a 19. Sudeste e Centro-Oeste tendem a apresentar comportamento mais precoce e concentrado; Nordeste exibiu picos mais tardios nos anos recentes; Norte e Sul foram mais variáveis.

A autocorrelação confirmou a dependência do passado: para Brasil, foi 0,987 em uma semana e permaneceu alta em 52 e 53 semanas. A sazonalidade, portanto, era uma hipótese empírica forte para os modelos. Ao mesmo tempo, médias e desvios-padrão cresceram juntos em algumas temporadas, indicando que a variabilidade não é constante.

Também apareceu uma diferença decisiva entre escalas geográficas. Treze UFs tiveram mais de 50% de semanas maduras sem casos. Para uma UF intermitente, uma previsão baseada em nível e tendência pode ser menos útil do que simplesmente repetir a última contagem em curtíssimo prazo. Brasil e regiões, mais densos, comportam-se de outra forma. Essa constatação direcionou toda a modelagem posterior.

## 5. A pandemia não foi apagada dos dados

As temporadas de 2020 e 2021 foram claramente diferentes. O total brasileiro foi 1.120 em 2020 e 11.124 em 2021, antes de crescer de 14.969 em 2022 para 43.152 em 2025. O estudo não transformou essas diferenças em uma explicação causal única: mudanças em transmissão, testagem, notificação, procura por serviços e vigilância podem ter contribuído.

A decisão foi preservar o histórico, sem remover anos manualmente, e usar validação temporal. A avaliação testa previsões em diferentes períodos históricos, em vez de pressupor que todas as temporadas sejam intercambiáveis. Isso é mais honesto com uma série que passou por ruptura tão relevante.

## 6. A comparação foi temporal, não aleatória

O calendário de avaliação foi definido antes dos modelos: 58 origens expansivas por série, com ao menos 156 semanas de treino inicial, quatro horizontes — 1, 4, 8 e 13 semanas — e nenhum uso de informação posterior à origem. Para Brasil e regiões, cada modelo produz 1.392 previsões comparáveis.

Esse desenho evita o vazamento temporal. Em séries temporais, dividir dados aleatoriamente permitiria que informações do futuro ajudassem a prever o passado, inflando artificialmente o desempenho. Também evita escolher um modelo somente porque ele foi bem em um único pico ou em uma única temporada.

## 7. Modelos simples tiveram direito de competir

O primeiro comparador foi o ingênuo, que repete o último valor observado. O segundo foi o ingênuo sazonal, que reutiliza a referência do ciclo anual anterior. Esses métodos parecem simples, mas são referências difíceis de vencer quando há persistência e sazonalidade.

Para Brasil e regiões, o ETS com tendência amortecida foi a melhor referência em 1 e 4 semanas. Sua inicialização precisou ser ajustada para evitar falhas de convergência; com a solução heurística, todos os 348 ajustes esperados convergiram. Nos horizontes de 8 e 13 semanas, contudo, a referência ingênua sazonal foi mais robusta. Essa foi uma descoberta útil: não havia evidência para forçar o ETS nos horizontes maiores.

O SARIMA clássico foi testado porque a exploração havia mostrado dependência temporal e sazonalidade. Porém, ele não alcançou cobertura suficiente nas origens e não foi incluído no ranking final. O SARIMAX com harmônicos anuais foi uma tentativa mais estável e convergiu, mas não superou as escolhas mais simples. A decisão de não adotá-lo não representa fracasso; é evidência de que complexidade adicional não trouxe ganho demonstrado neste problema.

## 8. A Base V2 foi uma decisão, não uma troca de dados

A Base V2 costuma gerar confusão porque seu nome pode sugerir uma nova base de microdados. Não é isso. Ela é a coleção das melhores previsões independentes por nível e horizonte, feitas sobre o mesmo painel maduro:

- Brasil e regiões: ETS amortecido em 1 e 4 semanas; ingênuo sazonal em 8 e 13;
- UFs: ingênuo em 1 e 4 semanas; ingênuo sazonal em 8 e 13.

Em curto prazo, essa decisão reduziu bastante a incoerência inicial entre agregados e folhas, mas não a eliminou. Isso era esperado: previsões feitas separadamente não têm obrigação matemática de somar corretamente. A Base V2 era, portanto, o ponto de partida justo para comparar métodos de reconciliação hierárquica.

## 9. Coerência não basta se ela produzir previsões impossíveis

Foram comparados bottom-up, top-down global, top-down sazonal, WLS estrutural e MinT. Todos respondem de maneiras diferentes à pergunta “como ajustar previsões para que as somas coincidam?”.

Bottom-up usa as UFs para formar região e Brasil. Top-down parte do agregado e distribui para as folhas. WLS estrutural e MinT buscam uma combinação ponderada entre todos os níveis. Esses métodos mostraram por que a escolha não pode ser baseada somente em coerência: bottom-up e top-down foram coerentes, mas não melhoraram uniformemente os erros; WLS estrutural e MinT sem restrição produziram contagens negativas em quantidade material.

Uma previsão negativa de internações não é comunicável. Cortá-la para zero depois da reconciliação pareceria simples, mas faria com que a soma das UFs deixasse de ser igual à região e ao Brasil. Esse problema exigiu uma solução que respeitasse simultaneamente as duas condições.

## 10. A escolha metodológica final foi MinT não negativo em curto prazo

O MinT estima a reconciliação considerando a estrutura de erros das previsões. Como as UFs têm séries intermitentes, a matriz de covariância empírica era deficiente de posto; portanto, a versão com shrinkage OAS foi necessária para estabilizar a inversão. Ainda assim, a versão sem restrição continuou gerando negativos.

Foi então resolvido um problema de otimização com as 27 UFs limitadas a valores não negativos. Regiões e Brasil são calculados pela matriz de agregação, de modo que não há truncamento posterior. As 232 otimizações previstas convergiram e a coerência ficou exata até tolerância numérica.

O resultado foi um compromisso, não uma vitória universal. Em 1 e 4 semanas, o MASE das UFs caiu de 1,145 para 1,133 e de 2,285 para 2,211. Em uma semana, as regiões também melhoraram de 0,545 para 0,534. Em contrapartida, Brasil isolado ficou ligeiramente pior em 1 e 4 semanas, e as regiões pioraram em 4 semanas. Essa troca foi registrada explicitamente.

Por isso, a política final não diz que MinT não negativo é sempre o melhor modelo. Ela diz:

- se a necessidade é um número nacional isolado em curto prazo, a Base V2 direta pode ter menor erro;
- se a necessidade é divulgar juntos UFs, regiões e Brasil, a política MinT não negativa em 1 e 4 semanas produz uma visão coerente e possível;
- em 8 e 13 semanas, a Base V2 sazonal já é coerente e não ganhou com reconciliação adicional.

## 11. A previsão operacional não foi tratada como prova de acerto

Depois da validação retrospectiva, a política foi aplicada à última semana madura, 19/07/2026. A execução gerou 132 previsões e foi computacionalmente íntegra: não houve valores negativos e as somas geográficas foram preservadas.

Entretanto, o diagnóstico de plausibilidade mostrou uma discordância incomum entre a previsão ETS direta do Brasil e a soma das previsões de UFs no curto prazo. O ajuste MinT para Brasil foi 129,2 casos em uma semana e 551,0 em quatro semanas, acima da faixa histórica usual de ajustes. Isso não foi corrigido manualmente, porque mudar a regra depois de ver a resposta seria seleção pós-hoc.

A decisão responsável foi manter a política retrospectivamente avaliada, mas sinalizar a aplicação operacional como cenário reconciliado sob alta discordância. O resultado ilustra o valor de auditar a previsão final, não apenas a média de erros do passado.

## 12. Incerteza é parte da resposta

As previsões pontuais foram acompanhadas de faixas empíricas de 80% e 95%, obtidas dos resíduos nos 58 cortes. A verificação leave-one-out encontrou cobertura de 76,9% a 78,4% para as faixas de 80% e de 89,7% a 93,1% para as faixas de 95%.

Esses números são próximos, mas inferiores, aos níveis nominais. Portanto, as faixas não foram apresentadas como garantia probabilística. Elas são uma referência operacional para perceber que a incerteza cresce fortemente com o horizonte. Em 8 e 13 semanas, devem orientar cenários de planejamento, e não prometer uma contagem futura precisa.

## 13. Onde o trabalho termina e o que ele deixa pronto

A Etapa 40 consolidou métricas, política por horizonte, previsão operacional, incerteza, alertas e limitações. Ela não recalculou nem selecionou um modelo novo. Essa decisão de encerrar a busca evita a tentação de continuar tentando métodos até encontrar um resultado visualmente conveniente.

O trabalho termina com uma cadeia completa e auditável:

1. fonte oficial congelada;
2. recorte de caso declarado;
3. deduplicação e maturidade documentadas;
4. exploração que justificou as hipóteses temporais;
5. validação sem vazamento;
6. comparação de modelos simples e complexos;
7. reconciliação hierárquica com não negatividade;
8. previsão operacional acompanhada de incerteza e alerta;
9. consolidação pronta para relatório e apresentação.

O próximo teste científico natural não é ajustar mais um modelo aos mesmos cortes. É aplicar a política previamente fixada quando houver semanas futuras maduras e avaliá-la em uma janela independente.
