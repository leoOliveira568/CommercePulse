# CommercePulse — Análise 360º de E-commerce Brasileiro

## Contexto do Problema
O projeto visa analisar uma base de dados real de e-commerce brasileiro para entender as principais métricas de negócio, como evolução do GMV, categorias mais vendidas, satisfação do cliente e associação do frete e do tempo de entrega com as avaliações.

## Fonte dos Dados
Os dados utilizados neste projeto são do **Olist Store**, o maior departamento de e-commerce do Brasil, disponíveis publicamente no [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

## Estrutura de Pastas
- `data/raw/`: Dados originais baixados do Kaggle.
- `data/processed/`: Dados transformados e limpos prontos para análise.
- `notebooks/`: Jupyter Notebooks utilizados para exploração e análise de dados.
- `dashboard/`: Dashboard interativo Streamlit consolidando métricas e análises.
- `reports/`: Relatório executivo com insights e recomendações.
- `src/`: Scripts Python auxiliares (geração de datasets, exportação de gráficos).

## Notebooks

| Notebook | Descrição |
|----------|-----------|
| `01_data_understanding.ipynb` | Entendimento inicial dos dados brutos |
| `02_exploratory_analysis.ipynb` | EDA completa com KPIs, gráficos e insights |
| `03_seller_delay_analysis.ipynb` | Análise de vendedores com concentração de atrasos |
| `04_rfm_segmentation.ipynb` | Segmentação de clientes por RFM (Recency, Frequency, Monetary) |

## Como Instalar as Dependências
O projeto é validado com **Python 3.11**. É recomendado criar um ambiente virtual antes de instalar as dependências.
```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Como Gerar a Base Processada
O dashboard funciona diretamente com os CSVs versionados em `data/processed/`. Para reproduzir o pipeline desde os dados brutos:

1. Baixe o conjunto **Brazilian E-Commerce Public Dataset by Olist** no link da seção “Fonte dos Dados”.
2. Extraia os CSVs originais, sem renomeá-los, em `data/raw/`.
3. Execute o script de criação do dataset a partir da raiz do projeto:
```bash
python src/make_dataset.py
```

Para gerar a tabela de segmentação RFM (necessária para a página de Clientes no dashboard):
```bash
python src/make_rfm_dataset.py
```

## Convenções Analíticas

- **GMV, volume e preço:** granularidade de item. GMV é o valor bruto dos itens dos pedidos e não equivale a receita contábil reconhecida.
- **Ticket, avaliação, prazo e atraso:** granularidade de pedido, sem dar peso extra a pedidos com vários itens.
- **Categorias:** avaliação e atraso contam uma vez por combinação pedido-categoria.
- **Vendedores:** logística usa pedido-vendedor; indica associação com atrasos, não causalidade.
- **RFM:** frequência usa o número real de compras (1, 2, 3, 4, 5+), preservando clientes empatados.

## Como Executar os Testes

```bash
python -m pytest
```

Os testes verificam granularidade, KPIs, métricas geográficas, categorias, vendedores e a lógica RFM.

## Como Rodar o Dashboard
Após instalar as dependências e gerar a base processada:
```bash
streamlit run dashboard/app.py
```
O dashboard será aberto automaticamente no navegador em `http://localhost:8501`.

### Páginas do Dashboard
- 📊 **Visão Geral** — KPIs principais, GMV mensal, tendências
- 🌎 **Geográfica** — Análise por estado, frete, satisfação regional
- 🏷️ **Categorias** — Top categorias, ticket médio, satisfação
- 🚚 **Logística** — Taxa de atraso, associação com a nota, tempo de entrega
- 🏪 **Vendedores** — Ranking de vendedores, análise de Pareto de atrasos
- 👥 **Clientes (RFM)** — Segmentação de clientes por Recência, Frequência e Valor

## Como Exportar Gráficos
Para gerar imagens PNG dos gráficos para relatórios:
```bash
python src/export_charts.py
```
As imagens serão salvas em `reports/charts/`.

## Relatório Executivo
O relatório executivo com storytelling dos insights está em `reports/executive_report.md`.

## Principais Insights
1. **Atraso está fortemente associado à satisfação** — Pedidos atrasados recebem nota 2,57 vs 4,29 dos entregues no prazo.
2. **Concentração geográfica** — SP, RJ e MG concentram 63,4% do GMV.
3. **Frete e avaliação** — Há associação negativa moderada entre frete médio e nota por estado (Pearson ≈ -0,39).
4. **Pareto de atrasos** — 13,7% dos vendedores estão associados a 80% dos pedidos atrasados.
5. **Baixa recompra** — 97,0% dos clientes fizeram apenas 1 compra; iniciativas de retenção devem ser validadas por experimento.
