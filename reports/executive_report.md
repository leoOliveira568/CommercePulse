# CommercePulse — Relatório Executivo

## Análise 360° do E-commerce Brasileiro (Olist)

**Período analisado:** Set/2016 — Ago/2018  
**Fonte dos dados:** Olist Store — Brazilian E-Commerce Public Dataset (Kaggle)  
**Autor:** CommercePulse Analytics

---

## 1. Resumo Executivo

O e-commerce brasileiro analisado apresenta **crescimento consistente de receita** ao longo dos 2 anos do período, com uma base de ~95 mil clientes únicos e ~99 mil pedidos processados por ~3 mil vendedores em 27 estados. A **logística é o principal ponto de dor**: 7,9% dos itens são entregues com atraso, e pedidos atrasados recebem notas significativamente inferiores. A **concentração geográfica** no Sudeste (SP, RJ, MG) domina a receita, mas estados emergentes apresentam alto potencial de crescimento. A **análise RFM** revela que a maioria dos clientes são de compra única, indicando uma grande oportunidade de retenção e recompra.

---

## 2. Panorama do E-commerce

### KPIs Principais

| Métrica | Valor |
|---------|-------|
| Total de pedidos | 98.666 |
| Total de itens vendidos | 112.650 |
| Receita total (produtos) | R$ 13.591.643,70 |
| Receita total (produtos + frete) | R$ 15.843.553,24 |
| Ticket médio por pedido | R$ 137,75 |
| Nota média dos clientes | 4,03 / 5,0 |
| Tempo médio de entrega | 12 dias |
| Taxa de atraso | 7,9% |
| Categorias de produto | 71 |
| Estados atendidos | 27 |
| Vendedores ativos | 3.095 |

### Evolução da Receita

A receita mensal apresentou **crescimento sustentado de Set/2016 a Ago/2018**, com:
- Picos sazonais em meses como **Novembro (Black Friday)** e **Janeiro**
- Estabilização em torno de **R$ 1 milhão/mês** a partir do 2º semestre de 2017
- Ticket médio relativamente estável entre R$ 120-150

---

## 3. Onde Estão os Clientes

### Concentração Geográfica

Os **3 estados do Sudeste** concentram a maior parte da atividade:

| Estado | % da Receita (aprox.) | Característica |
|--------|----------------------|----------------|
| **SP** | ~40% | Maior mercado, menor frete, entrega mais rápida |
| **RJ** | ~13% | Segundo maior mercado |
| **MG** | ~12% | Terceiro maior, bom ticket médio |

**Oportunidade:** Estados do Norte e Nordeste apresentam **ticket médio competitivo** mas são subatendidos em volume e sofrem com fretes mais altos e entregas mais longas.

### Frete e Satisfação

Existe uma **correlação negativa clara** entre frete médio e avaliação do cliente:
- Estados com **frete > R$ 30** tendem a ter notas médias abaixo de 4,0
- Estados com **frete < R$ 20** têm notas consistentemente acima de 4,0

---

## 4. O Que Mais Vende

### Top Categorias por Receita

As categorias que mais geram receita são:
1. **bed_bath_table** (cama, mesa e banho) — alto volume
2. **health_beauty** (beleza e saúde)  
3. **sports_leisure** (esportes e lazer)
4. **computers_accessories** (informática)
5. **furniture_decor** (móveis e decoração)

### Categorias de Alto Ticket

Categorias como **computers**, **watches_gifts** e **small_appliances** geram receita relevante com menos itens vendidos, indicando **alto ticket médio**. Já categorias como **bed_bath_table** dependem de volume.

---

## 5. Calcanhar de Aquiles: Logística

### Taxa de Atraso

- **7,9% dos itens** são entregues após a data estimada
- **Mediana do atraso:** ~7 dias além do prazo
- **Percentil 95:** atrasos chegam a 30+ dias

### Impacto na Satisfação

| Status | Nota Média |
|--------|------------|
| No prazo | ~4,3 ⭐ |
| Atrasado | ~2,5 ⭐ |

O atraso **reduz a nota em quase 2 pontos**, sendo o fator com maior impacto negativo na satisfação do cliente.

### Concentração dos Atrasos (Pareto)

A análise de Pareto revela que **poucos vendedores concentram a maioria dos atrasos**. Ações direcionadas a esse grupo teriam impacto desproporcional na melhoria da taxa de atraso global.

### Estados Mais Afetados

Estados do **Norte e Nordeste** apresentam as maiores taxas de atraso e os maiores tempos médios de entrega, refletindo desafios logísticos de infraestrutura e distância dos centros de distribuição (concentrados em SP).

---

## 6. Segmentação de Clientes (RFM)

A análise RFM segmentou os ~95 mil clientes em grupos de comportamento:

| Segmento | Descrição | Ação Recomendada |
|----------|-----------|------------------|
| **Champions** | Compraram recente, frequente, e gastam muito | Programa de fidelidade VIP |
| **Loyal Customers** | Compram com frequência e gastam bem | Cross-sell, recompensas por indicação |
| **New Customers** | Compraram recentemente pela primeira vez | Cupom de segunda compra, onboarding |
| **At Risk** | Costumavam comprar, mas pararam | Campanha de retenção urgente |
| **Hibernating** | Compraram há muito tempo, baixa frequência | Campanha de reativação com desconto |

**Achado principal:** A vasta maioria (~97%) dos clientes possui apenas **1 compra**, indicando que a taxa de recompra é extremamente baixa. Isso é típico de marketplaces, mas representa uma **grande oportunidade**: mesmo um pequeno aumento na taxa de recompra geraria receita incremental significativa.

---

## 7. Recomendações Estratégicas

### 🔴 Prioridade Alta

1. **Programa de monitoramento de vendedores com altos atrasos**
   - Implementar alertas automáticos para vendedores com taxa de atraso > 15%
   - Plano de ação progressivo: aviso → penalização de ranking → suspensão
   - **Impacto esperado:** Redução da taxa de atraso global em 30-50%

2. **Investir em infraestrutura logística para Norte e Nordeste**
   - Parcerias com centros de distribuição regionais
   - Opções de fulfillment para vendedores dessas regiões
   - **Impacto esperado:** Redução do tempo médio de entrega e aumento de satisfação

3. **Programa de incentivo à segunda compra**
   - Cupom de desconto para a segunda compra (enviado 7-14 dias após a primeira entrega)
   - Personalizado por categoria comprada
   - **Impacto esperado:** Aumento da taxa de recompra de 3% para 5-8%

### 🟡 Prioridade Média

4. **Estratégia de frete subsidiado para estados com alto potencial**
   - Frete grátis ou reduzido para clientes do Nordeste em compras acima de R$ 100
   - **Impacto esperado:** Aumento de conversão de 10-20% nesses estados

5. **Curadoria de categorias com baixa satisfação**
   - Investigar categorias com nota < 3,5 para problemas de qualidade ou descrição enganosa
   - Exigir fotos e descrições mais detalhadas de vendedores dessas categorias

### 🟢 Prioridade Baixa (Longo Prazo)

6. **Dashboard de performance para vendedores**
   - Portal self-service para vendedores acompanharem suas métricas
   - Benchmarking contra médias da categoria e estado

---

## 8. Próximos Passos Analíticos

- **Análise de coorte:** Acompanhar retenção de clientes por coorte mensal
- **Análise de NLP:** Extrair temas de insatisfação a partir das reviews textuais
- **Previsão de demanda:** Modelo de forecast de receita por categoria/estado
- **Análise de churn de vendedores:** Identificar fatores que levam à saída de vendedores do marketplace
- **Testes A/B:** Experimentar estratégias de frete e comunicação por segmento RFM

---

*Relatório gerado pelo CommercePulse Analytics — Julho 2026*
