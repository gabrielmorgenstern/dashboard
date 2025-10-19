
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard de Produtos", page_icon="📊", layout="wide")

# ---------------------------
# Funções utilitárias
# ---------------------------
def to_number_br(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float, np.number)):
        return float(x)
    s = str(x).strip()
    is_percent = s.endswith("%")
    s = s.replace("%", "").replace(".", "").replace(",", ".")
    try:
        val = float(s)
        if is_percent:
            return val / 100.0
        return val
    except Exception:
        return np.nan

def load_data(uploaded_file):
    if uploaded_file is None:
        st.info("Faça o upload do arquivo Excel (.xlsx) com seus dados.")
        st.stop()
    df = pd.read_excel(uploaded_file)
    return df

def _prepare_png(fig, width=1400, height=800):
    """Cria uma cópia da figura com dimensões e margens adequadas para exportação em PNG."""
    fig2 = go.Figure(fig)  # cópia
    fig2.update_layout(
        width=width, height=height, autosize=False,
        margin=dict(l=200, r=60, t=90, b=90),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    fig2.update_xaxes(automargin=True)
    fig2.update_yaxes(automargin=True)
    return fig2

def fig_download_button(fig, filename, label="Baixar gráfico (PNG)"):
    try:
        fig2 = _prepare_png(fig)
        png = fig2.to_image(format="png", width=fig2.layout.width, height=fig2.layout.height, scale=2)
        st.download_button(
            label=label,
            data=png,
            file_name=filename,
            mime="image/png",
            use_container_width=True
        )
    except Exception as e:
        st.caption("Para exportar PNG, instale a dependência: `pip install -U kaleido`.")

# ---------------------------
# Sidebar - Upload e Filtros
# ---------------------------
st.sidebar.title("⚙️ Configurações")
uploaded = st.sidebar.file_uploader("Envie a planilha (.xlsx)", type=["xlsx"])

PALETTE = px.colors.sequential.Blues
df_raw = load_data(uploaded)

# ---------------------------
# Mapeamento de colunas
# ---------------------------
COLS = {
    "produto": "Produto",
    "sku": "SKU da Variação",
    "views": "Visualizações da Página do Produto",
    "sessions": "Visitantes do Produto (Visita)",
    "bounce_rate": "Taxa de Rejeição do Produto",
    "clicks_search": "Cliques em buscas",
    "add_to_cart_visitors": "Visitantes do Produto (Adicionar ao Carrinho)",
    "add_to_cart_units": "Unidades (adicionar ao carrinho)",
    "conv_add_to_cart": "Taxa de Conversão (adicionar ao carrinho)",
    "buyers_ordered": "Compradores (Pedido realizado)",
    "units_ordered": "Unidades (Pedido realizado)",
    "revenue_ordered": "Vendas (Pedido realizado) (BRL)",
    "conv_ordered": "Taxa de conversão (Pedido realizado)",
    "buyers_paid": "Compradores (Pedidos pago)",
    "units_paid": "Unidades (Pedido pago)",
    "revenue_paid": "Vendas (Pedido pago) (BRL)",
    "conv_paid": "Taxa de conversão (Pedido pago)",
}

missing = [v for v in COLS.values() if v not in df_raw.columns]
if missing:
    st.error("Colunas esperadas não encontradas:\n\n- " + "\n- ".join(missing))
    st.stop()

# ---------------------------
# Conversões numéricas
# ---------------------------
df = df_raw.copy()
num_cols = [
    COLS["views"], COLS["sessions"], COLS["add_to_cart_visitors"],
    COLS["add_to_cart_units"], COLS["buyers_ordered"], COLS["units_ordered"],
    COLS["revenue_ordered"], COLS["buyers_paid"], COLS["units_paid"], COLS["revenue_paid"],
    COLS["conv_add_to_cart"], COLS["conv_ordered"], COLS["conv_paid"], COLS["bounce_rate"]
]
for c in num_cols:
    df[c] = df[c].apply(to_number_br)

# ---------------------------
# Filtros
# ---------------------------
all_products = df[COLS["produto"]].dropna().astype(str).unique().tolist()
selected_products = st.sidebar.multiselect("Filtrar produtos", options=all_products, default=all_products)
df = df[df[COLS["produto"]].astype(str).isin(selected_products)]

default_product = None
if not df.empty:
    default_product = df.sort_values(by=COLS["views"], ascending=False)[COLS["produto"]].iloc[0]

# ---------------------------
# KPIs (ADICIONADO: Ticket médio no painel principal)
# ---------------------------
total_revenue = df[COLS["revenue_paid"]].sum(skipna=True)
total_units = df[COLS["units_paid"]].sum(skipna=True)
total_sessions = df[COLS["sessions"]].sum(skipna=True)
total_buyers = df[COLS["buyers_paid"]].sum(skipna=True)

overall_conv = (total_buyers / total_sessions) if total_sessions else np.nan
ticket_medio_overall = (total_revenue / total_buyers) if total_buyers else np.nan

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Vendas pagas (R$)", f"{total_revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col2.metric("📦 Unidades pagas", f"{int(total_units):,}".replace(",", "."))
col3.metric("👥 Sessões (produtos)", f"{int(total_sessions):,}".replace(",", "."))
col4.metric("✅ Conversão geral", f"{(overall_conv if pd.notna(overall_conv) else 0)*100:,.2f}%".replace(",", "X").replace(".", ",").replace("X", "."))
col5.metric("🎟️ Ticket médio (R$)", f"{(ticket_medio_overall if pd.notna(ticket_medio_overall) else 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")

# ---------------------------
# Gráfico principal
# ---------------------------
st.subheader("📈 Visão por produto")

metric_map = {
    "Unidades vendidas": COLS["units_paid"],
    "Valor de pedidos pagos": COLS["revenue_paid"],
    "Taxa de conversão": "__conv_calc__",  # calculada robusta
    "Ticket médio (pedido pago)": "__ticket_medio__",
    "Receita por sessão": "__rps__",
}
metric_label = st.selectbox("Selecione a métrica para o gráfico", list(metric_map.keys()), index=0)
max_items = st.slider("Quantidade de produtos exibidos no gráfico", min_value=5, max_value=50, value=15, step=5)

agg = {
    COLS["units_paid"]: "sum",
    COLS["revenue_paid"]: "sum",
    COLS["buyers_paid"]: "sum",
    COLS["sessions"]: "sum",
}
g = df.groupby(COLS["produto"], as_index=False).agg(agg)

g["__conv_calc__"] = np.where(g[COLS["sessions"]].fillna(0) > 0,
                              g[COLS["buyers_paid"]] / g[COLS["sessions"]],
                              np.nan)
g["__ticket_medio__"] = np.where(g[COLS["buyers_paid"]].fillna(0) > 0,
                                 g[COLS["revenue_paid"]] / g[COLS["buyers_paid"]],
                                 np.nan)
g["__rps__"] = np.where(g[COLS["sessions"]].fillna(0) > 0,
                        g[COLS["revenue_paid"]] / g[COLS["sessions"]],
                        np.nan)

g["__metric__"] = g[metric_map[metric_label]]
g = g.sort_values("__metric__", ascending=False).head(max_items)

if metric_label == "Taxa de conversão":
    hover_template = "%{y}<br>%{x:.2%}<extra></extra>"
    x_title = "Taxa de conversão"
elif metric_label in ["Ticket médio (pedido pago)", "Receita por sessão", "Valor de pedidos pagos"]:
    hover_template = "%{y}<br>R$ %{x:,.2f}<extra></extra>"
    x_title = metric_label
else:
    hover_template = "%{y}<br>%{x:,.2f}<extra></extra>"
    x_title = metric_label

fig = px.bar(
    g, x="__metric__", y=COLS["produto"],
    orientation="h",
    title=f"{metric_label} por produto (top {len(g)})",
    color="__metric__", color_continuous_scale=px.colors.sequential.Blues,
)
fig.update_traces(hovertemplate=hover_template)
fig.update_layout(xaxis_title=x_title, yaxis_title="Produto", height=650, margin=dict(l=10, r=10, t=60, b=10))

st.plotly_chart(fig, use_container_width=True)
def safe_slug(s): 
    return str(s).strip().lower().replace(" ", "_").replace("/", "-")
fig_download_button(fig, filename=f"grafico_{safe_slug(metric_label)}.png")

# ---------------------------
# Funil por produto
# ---------------------------
st.markdown("---")
st.subheader("🔻 Funil por produto")

product_for_funnel = st.selectbox(
    "Selecione o produto para analisar o funil",
    all_products,
    index=(all_products.index(default_product) if default_product in all_products else 0) if all_products else 0
)
df_one = df[df[COLS["produto"]].astype(str) == str(product_for_funnel)].copy()

if df_one.empty:
    st.info("Produto sem dados para o funil.")
else:
    steps = {
        "Visualizações": df_one[COLS["views"]].sum(skipna=True),
        "Adicionar ao carrinho (visitantes)": df_one[COLS["add_to_cart_visitors"]].sum(skipna=True),
        "Pedidos realizados (compradores)": df_one[COLS["buyers_ordered"]].sum(skipna=True),
        "Pedidos pagos (compradores)": df_one[COLS["buyers_paid"]].sum(skipna=True),
    }
    funnel_df = pd.DataFrame({"Etapa": list(steps.keys()), "Quantidade": list(steps.values())})

    funnel_fig = go.Figure(go.Funnel(
        y=funnel_df["Etapa"],
        x=funnel_df["Quantidade"],
        textposition="inside",
        textinfo="value+percent previous",
        marker={"color": px.colors.sequential.Blues[-2]},
    ))
    funnel_fig.update_layout(
        title=f"Funil de conversão — {product_for_funnel}",
        height=500, margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(funnel_fig, use_container_width=True)
    fig_download_button(funnel_fig, filename=f"funil_{safe_slug(product_for_funnel)}.png")

# ---------------------------
# Tabela de “itens com maior valor de pedidos pagos”
# ---------------------------
st.markdown("---")
st.subheader("🏆 Itens por maior valor de pedidos pagos")

top_n = st.slider("Quantidade de itens no ranking", min_value=5, max_value=50, value=10, step=5)
ranking = (
    df[[COLS["produto"], COLS["sku"], COLS["revenue_paid"], COLS["units_paid"]]]
    .groupby([COLS["produto"], COLS["sku"]], as_index=False)
    .sum()
    .sort_values(COLS["revenue_paid"], ascending=False)
    .head(top_n)
)

ranking_display = ranking.copy()
ranking_display["Vendas Pagas (R$)"] = ranking_display[COLS["revenue_paid"]].map(
    lambda v: f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)
ranking_display["Unidades Pagas"] = ranking_display[COLS["units_paid"]].astype(int)
ranking_display = ranking_display.rename(
    columns={COLS["produto"]: "Produto", COLS["sku"]: "SKU"}
)[["Produto", "SKU", "Unidades Pagas", "Vendas Pagas (R$)"]]

st.dataframe(ranking_display, use_container_width=True)

st.caption("Desenvolvido por Gabriel Morgenstern")
