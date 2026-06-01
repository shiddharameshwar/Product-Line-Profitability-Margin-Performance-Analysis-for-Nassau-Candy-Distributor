import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    layout="wide"
)

st.title("📊 Nassau Candy Profitability Dashboard")

# =========================
# DATA LOADER
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("nassau.csv")

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert dates safely
    for col in ['Order Date', 'Ship Date']:
        df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')

    # Remove bad rows
    df.dropna(subset=['Order Date', 'Ship Date'], inplace=True)

    return df

# =========================
# LOAD DATA (CRITICAL)
# =========================
df = load_data()

# =========================
# BASIC CLEANING
# =========================
df = df[df['Sales'] > 0]
df = df[df['Units'] > 0]

# =========================
# FEATURE ENGINEERING
# =========================
df['Gross Profit'] = df['Sales'] - df['Cost']

df['Gross Margin %'] = (
    df['Gross Profit'] / df['Sales']
) * 100

df['Profit per Unit'] = (
    df['Gross Profit'] / df['Units']
)

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("Filters")

division_filter = st.sidebar.multiselect(
    "Select Division",
    df['Division'].unique(),
    default=df['Division'].unique()
)

margin_threshold = st.sidebar.slider(
    "Minimum Margin %",
    -100, 100, 0
)

# Apply filters
df = df[
    (df['Division'].isin(division_filter)) &
    (df['Gross Margin %'] >= margin_threshold)
]

# =========================
# KPI CALCULATIONS
# =========================
total_sales = df['Sales'].sum()
total_profit = df['Gross Profit'].sum()
total_units = df['Units'].sum()
avg_margin = df['Gross Margin %'].mean()

# =========================
# KPI UI
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Total Profit", f"${total_profit:,.0f}")
col3.metric("Avg Margin", f"{avg_margin:.2f}%")
col4.metric("Total Units", f"{total_units:,.0f}")

# =========================
# PRODUCT ANALYSIS
# =========================
st.subheader("🏆 Top Products")

product_df = df.groupby("Product Name").agg({
    "Sales": "sum",
    "Gross Profit": "sum",
    "Gross Margin %": "mean"
}).reset_index()

product_df = product_df.sort_values("Gross Profit", ascending=False)

fig = px.bar(
    product_df.head(10),
    x="Gross Profit",
    y="Product Name",
    orientation="h",
    color="Gross Margin %"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# DIVISION ANALYSIS
# =========================
st.subheader("📊 Division Performance")

division_df = df.groupby("Division").agg({
    "Sales": "sum",
    "Gross Profit": "sum"
}).reset_index()

fig2 = px.bar(
    division_df,
    x="Division",
    y=["Sales", "Gross Profit"],
    barmode="group"
)

st.plotly_chart(fig2, use_container_width=True)

# =========================
# COST VS MARGIN
# =========================
st.subheader("💰 Cost vs Margin")

fig3 = px.scatter(
    df,
    x="Cost",
    y="Gross Margin %",
    color="Division",
    size="Sales",
    hover_name="Product Name"
)

st.plotly_chart(fig3, use_container_width=True)

# =========================
# PARETO ANALYSIS
# =========================
st.subheader("📈 Pareto Analysis")

pareto = product_df.sort_values("Gross Profit", ascending=False)
pareto["Cumulative %"] = pareto["Gross Profit"].cumsum() / pareto["Gross Profit"].sum() * 100

fig4 = px.bar(
    pareto.head(20),
    x="Product Name",
    y="Gross Profit"
)

st.plotly_chart(fig4, use_container_width=True)

# =========================
# RAW DATA VIEW
# =========================
st.subheader("📄 Data Preview")

st.dataframe(df.head(50))