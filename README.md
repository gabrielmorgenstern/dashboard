# Dashboard Streamlit de Produtos

## Descrição do Projeto

Dashboard interativo desenvolvido em Python usando **Streamlit** para análise de desempenho de produtos a partir de dados em planilha Excel (.xlsx). Facilita o monitoramento de métricas chave (KPIs) e permite gerar gráficos e relatórios visualmente intuitivos.

---

## Campos Necessários na Planilha Excel

O arquivo de entrada deve conter as seguintes colunas obrigatórias:

- Produto
- SKU da Variação
- Visualizações da Página do Produto
- Visitantes do Produto (Visita)
- Taxa de Rejeição do Produto
- Cliques em buscas
- Visitantes do Produto (Adicionar ao Carrinho)
- Unidades (adicionar ao carrinho)
- Taxa de Conversão (adicionar ao carrinho)
- Compradores (Pedido realizado)
- Unidades (Pedido realizado)
- Vendas (Pedido realizado) (BRL)
- Taxa de conversão (Pedido realizado)
- Compradores (Pedidos pago)
- Unidades (Pedido pago)
- Vendas (Pedido pago) (BRL)
- Taxa de conversão (Pedido pago)

---

## KPIs Utilizados no Dashboard

- **Vendas pagas (R$):** Soma das vendas concretizadas.
- **Unidades pagas:** Total de unidades vendidas com pagamento confirmado.
- **Sessões (produtos):** Total de visitantes únicos dos produtos.
- **Conversão geral:** Percentual de compradores pagos sobre sessões totais (compradores/sessões).
- **Ticket médio:** Receita média por comprador (vendas pagas / compradores).

---

## Funcionalidades Principais

- Upload da planilha Excel com validação das colunas.
- Filtragem interativa por produto.
- Visualização de métricas principais em painel de KPIs.
- Gráficos de barras interativos com métricas selecionáveis por produto.
- Funil de conversão detalhado dos produtos.
- Tabela dinâmica dos produtos com maior valor de vendas pagas.
- Exportação dos gráficos em PNG para relatório.

---

## Tecnologias e Bibliotecas

- Python 3.x
- Streamlit
- Pandas
- Numpy
- Plotly
- Kaleido (opcional para exportação em PNG)

---

## Como Usar

1. Execute o dashboard:
```
streamlit run dashboard_streamlit.py
```
2. Faça upload da planilha Excel formatada.
3. Explore os KPIs e gráficos.
4. Exporte dados e gráficos conforme necessário.

---

## Contato

Para dúvidas e suporte: gabriel.betarj@gmail.com

---

## Licença

Projeto para uso pessoal e educacional. Redistribuições precisam de autorização.

