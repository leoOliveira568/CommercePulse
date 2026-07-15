# CommercePulse — Análise 360º de E-commerce Brasileiro

## Contexto do Problema
O projeto visa analisar uma base de dados real de e-commerce brasileiro para entender as principais métricas de negócio, como evolução da receita, categorias mais vendidas, satisfação do cliente, impacto do frete e do tempo de entrega nas avaliações.

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
É recomendado criar um ambiente virtual antes de instalar as dependências.
```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Como Gerar a Base Processada
Execute o script de criação do dataset a partir da raiz do projeto:
```bash
python src/make_dataset.py
```

Para gerar a tabela de segmentação RFM (necessária para a página de Clientes no dashboard):
```bash
python src/make_rfm_dataset.py
```

## Como Rodar o Dashboard
Após instalar as dependências e gerar a base processada:
```bash
streamlit run dashboard/app.py
```
O dashboard será aberto automaticamente no navegador em `http://localhost:8501`.

### Páginas do Dashboard
- 📊 **Visão Geral** — KPIs principais, receita mensal, tendências
- 🌎 **Geográfica** — Análise por estado, frete, satisfação regional
- 🏷️ **Categorias** — Top categorias, ticket médio, satisfação
- 🚚 **Logística** — Taxa de atraso, impacto na nota, tempo de entrega
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
1. **Atraso impacta diretamente a satisfação** — Pedidos atrasados recebem nota ~2,5 vs ~4,3 dos entregues no prazo.
2. **Concentração geográfica** — SP, RJ e MG concentram ~65% da receita.
3. **Frete alto ↔ nota baixa** — Estados com frete > R$ 30 têm notas consistentemente inferiores.
4. **Pareto de atrasos** — Poucos vendedores concentram a maioria dos atrasos.
5. **Baixa recompra** — ~97% dos clientes fizeram apenas 1 compra, grande oportunidade de retenção.
