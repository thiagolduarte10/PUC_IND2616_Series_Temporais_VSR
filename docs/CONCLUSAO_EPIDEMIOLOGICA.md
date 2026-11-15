# Conclusão epidemiológica — versão vigente após a etapa 43

Atualização documental: 14/11/2026.

## O que a série representa

O estudo prevê contagens semanais de notificações de crianças menores de dois anos, hospitalizadas por SRAG e com confirmação específica de VSR. A semana é a de início de sintomas; a geografia é a de residência. Portanto, não são previsões diretas de ocupação de leitos, de admissões por data de internação ou de atendimento no hospital situado naquela UF.

A base madura contém 155.304 notificações em 395 semanas. Sazonalidade e diferenças regionais aparecem nos registros. Treze UFs têm mais de 50% de semanas zero, sem que isso demonstre ausência de circulação viral. Variações de volume não devem ser interpretadas como taxas populacionais: o estudo não utilizou denominadores do SINASC.

## O que se pode concluir

Os registros apresentam padrões temporais úteis para previsão, mas com mudanças de intensidade e timing entre temporadas e regiões. A ruptura de 2020–2021 pode combinar circulação, procura por assistência, testagem e notificação. O desenho não identifica a contribuição causal de cada fator.

A maturidade de 13 semanas reduz o uso de registros recentes incompletos. Ela também impõe uma limitação prática: a aplicação parte de uma origem antiga, 19/07/2026. Não há nowcasting preenchendo a distância até o presente. Antes de uso corrente, seria necessário atualizar dados e avaliar atrasos.

## Como a extensão alterou a conclusão preditiva

As etapas 41–43 acrescentaram modelos intermitentes, um GLM de contagens e LightGBM compartilhado entre séries. A política vigente combina ETS e LightGBM das UFs em 1/4 semanas; nos horizontes maiores combina referências sazonais e LightGBM global. Todos passam por MinT-OAS não negativo.

Houve melhora de MASE em 11 das 12 combinações de nível e horizonte frente à política anterior, com pequena piora regional em 13 semanas. Isso é evidência retrospectiva de potencial preditivo, não demonstração de benefício assistencial ou redução de internações.

## Aplicação ilustrativa

| Horizonte | Semana-alvo | Brasil: previsão | Faixa empírica 80% | Faixa empírica 95% |
|---|---|---:|---:|---:|
| 1 | 26/07/2026 | 683,2 | 634,9–756,3 | 553,8–844,8 |
| 4 | 16/08/2026 | 329,2 | 176,7–677,3 | 134,1–941,3 |
| 8 | 13/09/2026 | 190,0 | 6,8–737,2 | 0–1.288,8 |
| 13 | 18/10/2026 | 88,0 | 0–598,0 | 0–1.080,7 |

Esses números são cenários emitidos a partir de 19/07/2026 para semanas-alvo específicas, e não previsões para novembro ou acumulados de quatro, oito e 13 semanas.

A etapa 43 não registrou ajustes acima do P95 histórico no teste de plausibilidade implementado. Isso substitui o alerta como descrição da saída atual, mas não elimina os riscos epidemiológicos nem demonstra acerto da projeção. As faixas longas continuam amplas, são marginais e têm cobertura retrospectiva inferior à nominal.

## Uso possível e limites

O potencial é apoiar discussão de preparação assistencial regional, em conjunto com vigilância, ocupação, oferta de serviços e conhecimento local. Uma contagem por residência e início dos sintomas não se converte automaticamente em necessidade de leitos: seriam necessários local de atendimento, duração da internação, gravidade e capacidade instalada.

A seleção dos modelos e da política reutiliza as mesmas 58 origens usadas para calcular as métricas. Os ganhos podem estar otimistas; a magnitude desse viés não foi estimada. Não há teste final intocado nem demonstração de significância estatística. A calibração do MinT atravessa 2020–2021. A validação usa uma versão consolidada dos registros: separar datas de treino e alvo evita o uso direto de alvos futuros no ajuste, mas não reconstitui exatamente o que estava publicado em cada origem histórica. A maturidade de 13 semanas reduz o problema das semanas recentes; não substitui snapshots históricos ou uma avaliação em tempo real.

O estudo não estima risco clínico individual, impacto de vacinação ou eficácia de intervenções. A conclusão defensável é que a combinação de modelos-base e reconciliação oferece previsões coerentes e promissoras para a vigilância de registros hospitalares de VSR. O uso decisório exige avaliação futura independente e integração com a informação assistencial.
