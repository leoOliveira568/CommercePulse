# CommercePulse — Relatório Executivo

## Análise 360° do E-commerce Brasileiro (Olist)

**Período analisado:** Set/2016 — Ago/2018  
**Fonte dos dados:** Olist Store — Brazilian E-Commerce Public Dataset (Kaggle)  
**Autor:** CommercePulse Analytics

---

## 1. Resumo Executivo

O e-commerce brasileiro analisado apresenta forte expansão entre 2016 e 2018, com estabilização do volume mensal no último ano completo, uma base de ~95 mil clientes únicos e ~99 mil pedidos processados por ~3 mil vendedores em 27 estados. A **logística é um ponto relevante de atenção**: 8,1% dos pedidos entregues chegam após a data estimada, e esses pedidos estão associados a avaliações substancialmente inferiores. A **concentração geográfica** no Sudeste (SP, RJ, MG) representa 63,4% do GMV. A **análise RFM** mostra que 97,0% dos clientes entregues fizeram uma única compra, indicando oportunidade de testar iniciativas de retenção e recompra.

---

## 2. Panorama do E-commerce

### KPIs Principais

| Métrica | Valor |
|---------|-------|
| Total de pedidos | 98.666 |
| Total de itens vendidos | 112.650 |
| GMV dos produtos | R$ 13.591.643,70 |
| GMV dos produtos + frete | R$ 15.843.553,24 |
| Ticket médio por pedido | R$ 137,75 |
| Nota média por pedido avaliado | 4,11 / 5,0 |
| Tempo médio de entrega por pedido | 12,1 dias |
| Taxa de atraso por pedido entregue | 8,1% |
| Categorias de produto | 71 |
| Estados atendidos | 27 |
| Vendedores ativos | 3.095 |

### Evolução do GMV

O GMV mensal apresentou forte crescimento até o início de 2018 e depois estabilização, com:
- Picos sazonais em meses como **Novembro (Black Friday)** e **Janeiro**
- GMV próximo de **R$ 0,85–1,0 milhão/mês** entre fevereiro e agosto de 2018
- Ticket médio relativamente estável entre R$ 120-150

---

## 3. Onde Estão os Clientes

### Concentração Geográfica

Os **3 estados do Sudeste** concentram a maior parte da atividade:

| Estado | % do GMV | Característica |
|--------|----------------------|----------------|
| **SP** | 38,3% | Maior mercado, menor frete e entrega mais rápida |
| **RJ** | 13,4% | Segundo maior mercado |
| **MG** | 11,7% | Terceiro maior mercado |

**Oportunidade:** Estados do Norte e Nordeste apresentam **ticket médio competitivo** mas são subatendidos em volume e sofrem com fretes mais altos e entregas mais longas.

### Frete e Satisfação

Existe uma **associação negativa moderada** entre frete médio por pedido e avaliação média por estado (correlação de Pearson ≈ -0,39). O resultado é descritivo e não demonstra causalidade; distância, prazo e composição regional de produtos podem explicar parte da relação.

---

## 4. O Que Mais Vende

### Top Categorias por GMV

As categorias com maior GMV são:
1. **health_beauty** (beleza e saúde) — R$ 1,26 milhão
2. **watches_gifts** (relógios e presentes) — R$ 1,21 milhão
3. **bed_bath_table** (cama, mesa e banho) — R$ 1,04 milhão
4. **sports_leisure** (esportes e lazer) — R$ 988 mil
5. **computers_accessories** (informática) — R$ 912 mil

### Categorias de Alto Ticket

Categorias como **computers**, **watches_gifts** e **small_appliances** geram GMV relevante com menos itens vendidos, indicando **alto ticket médio**. Já categorias como **bed_bath_table** dependem de volume.

---

## 5. Calcanhar de Aquiles: Logística

### Taxa de Atraso

- **8,1% dos pedidos entregues** chegam após a data estimada
- **Mediana do atraso:** 5 dias além do prazo
- **Percentil 95:** 29 dias de atraso

### Associação com a Satisfação

| Status | Nota Média |
|--------|------------|
| No prazo | 4,29 ⭐ |
| Atrasado | 2,57 ⭐ |

Pedidos atrasados apresentam nota média **1,73 ponto inferior**. A diferença é forte, mas a base observacional permite afirmar associação, não causalidade isolada.

### Concentração dos Atrasos (Pareto)

A análise de Pareto mostra que **423 vendedores (13,7% do total) estão associados a 80% dos pedidos atrasados**. Como a data de entrega está no nível do pedido, essa associação não prova que o vendedor causou o atraso; transportadora, rota e pedidos com múltiplos vendedores também podem influenciar o resultado.

### Estados Mais Afetados

Diversos estados do **Norte e Nordeste** apresentam taxas de atraso e tempos médios de entrega elevados. A base não permite atribuir diretamente o resultado à infraestrutura ou à distância; essas hipóteses devem ser verificadas com dados de rota, transportadora e centros de distribuição.

---

## 6. Segmentação de Clientes (RFM)

A análise RFM segmentou 93.358 clientes com pedidos entregues. A frequência usa faixas reais de compras, evitando separar arbitrariamente clientes empatados:

| Segmento | Clientes | Ação Recomendada |
|----------|---------:|------------------|
| **Champions** | 33 | Programa VIP e entrevistas qualitativas |
| **Loyal Customers** | 124 | Cross-sell e recompensas por indicação |
| **Potential Loyalists** | 37.577 | Teste de incentivo à segunda/terceira compra |
| **New Customers** | 14.605 | Onboarding e cupom de segunda compra |
| **At Risk** | 62 | Campanha controlada de reativação |
| **Hibernating** | 37.154 | Teste de reativação com limite de custo |
| **Others** | 3.803 | Monitoramento e comunicação contextual |

**Achado principal:** 97,0% dos clientes possuem apenas **1 compra entregue**. Isso pode refletir baixa retenção, mas também limitações do período observado e compras como convidado; o impacto de campanhas deve ser medido por teste controlado e margem incremental.

---

## 7. Recomendações Estratégicas

### 🔴 Prioridade Alta

1. **Programa de monitoramento de vendedores com altos atrasos**
   - Implementar alertas automáticos para vendedores com taxa de atraso > 15%
   - Plano de ação progressivo: aviso → penalização de ranking → suspensão
   - **Métrica de sucesso:** redução da taxa de atraso por pedido, controlada por rota e transportadora

2. **Investir em infraestrutura logística para Norte e Nordeste**
   - Parcerias com centros de distribuição regionais
   - Opções de fulfillment para vendedores dessas regiões
   - **Métrica de sucesso:** prazo, atraso e avaliação comparados a regiões-controle

3. **Programa de incentivo à segunda compra**
   - Cupom de desconto para a segunda compra (enviado 7-14 dias após a primeira entrega)
   - Personalizado por categoria comprada
   - **Métrica de sucesso:** recompra incremental, margem e custo por cliente reativado

### 🟡 Prioridade Média

4. **Estratégia de frete subsidiado para estados com alto potencial**
   - Frete grátis ou reduzido para clientes do Nordeste em compras acima de R$ 100
   - **Métrica de sucesso:** conversão e margem incremental em teste A/B regional

5. **Curadoria de categorias com baixa satisfação**
   - Investigar categorias com nota < 3,5 para problemas de qualidade ou descrição enganosa
   - Exigir fotos e descrições mais detalhadas de vendedores dessas categorias

### 🟢 Prioridade Baixa (Longo Prazo)

6. **Dashboard de performance para vendedores**
   - Portal self-service para vendedores acompanharem suas métricas
   - Benchmarking contra médias da categoria e estado

---

## 8. Notas Metodológicas

- GMV, volume e preço são calculados no nível do item; ticket, avaliação, prazo e atraso são calculados no nível do pedido. O GMV não representa receita contábil reconhecida.
- Em análises por categoria, cada pedido-categoria contribui uma vez para avaliação e atraso.
- Em análises por vendedor, a unidade logística é pedido-vendedor; isso representa associação e não atribuição causal do atraso.
- Pedidos sem entrega observada são excluídos dos indicadores logísticos, mas permanecem nos indicadores gerais de vendas.
- Os resultados descrevem a base Olist de 2016–2018 e não devem ser generalizados automaticamente para o mercado atual.

---

## 9. Próximos Passos Analíticos

- **Análise de coorte:** Acompanhar retenção de clientes por coorte mensal
- **Análise de NLP:** Extrair temas de insatisfação a partir das reviews textuais
- **Previsão de demanda:** Modelo de forecast de GMV por categoria/estado
- **Análise de churn de vendedores:** Identificar fatores que levam à saída de vendedores do marketplace
- **Testes A/B:** Experimentar estratégias de frete e comunicação por segmento RFM

---

*Relatório gerado pelo CommercePulse Analytics — Julho 2026*
