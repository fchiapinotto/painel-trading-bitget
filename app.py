import streamlit as st
from datetime import datetime
from fetch_data import get_all_timeframes
from indicators import extract_info
from analysis import render_analysis_section
from utils import render_price_card, render_indicators_table, render_legend

# === Configuração da página
st.set_page_config(page_title="Painel BTC/USDT", layout="wide")

# === Estilo
st.markdown("""
    <style>
    .titulo-secao {
        font-size: 28px; font-weight: bold; margin-bottom: 10px;
    }
    .card-btc {
        border: 2px solid #ccc;
        padding: 30px 0 10px;
        text-align: center;
        background: #f9f9f9;
        height: 158px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .card-preco {
        font-size: 52px;
    }
    .card-var {
        font-size: 22px;
        font-weight: 600;
        padding: 5px 10px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 10px;
    }
    .var-up { color: green; }
    .var-down { color: red; }
    .var-neutral { color: orange; }
    table {
        width: 100%;
        font-size: 16px;
        border-collapse: collapse;
    }
    th, td {
        text-align: center;
        padding: 10px;
        white-space: nowrap;
    }
    th {
        background-color: #f0f0f0;
    }
    </style>
""", unsafe_allow_html=True)

# === Carregar dados
df_1h, df_4h, df_1d = get_all_timeframes()
if df_1h is None or df_4h is None or df_1d is None:
    st.error("❌ Erro ao carregar dados da API Bitget.")
    st.stop()

# === Extrair informações
i1d, i4h, i1h = extract_info(df_1d), extract_info(df_4h), extract_info(df_1h)
last_price = df_1h["close"].iloc[-1]
var_pct = ((last_price - df_1h["close"].iloc[-2]) / df_1h["close"].iloc[-2]) * 100
var_icon = "🔼" if var_pct > 0 else "🔽" if var_pct < 0 else "➖"
var_class = "var-up" if var_pct > 0 else "var-down" if var_pct < 0 else "var-neutral"

# === Layout superior
col1, col2 = st.columns([1.2, 3])
with col1:
    st.markdown("<div class='titulo-secao'>💰 BTC Agora</div>", unsafe_allow_html=True)
    render_price_card(last_price, var_pct, var_icon, var_class)

with col2:
    render_analysis_section(df_1h, df_4h, df_1d)

# === Tabela de Indicadores
st.markdown("<div class='titulo-secao'>📊 Indicadores Técnicos</div>", unsafe_allow_html=True)
render_indicators_table(i1d, i4h, i1h)

# === Legenda
render_legend()
