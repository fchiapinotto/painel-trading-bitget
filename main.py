import streamlit as st
from datetime import datetime

from styles import set_custom_styles
from fetch_data import fetch_and_process_candles
from indicators import compute_indicators
from extract_info import extract_info
from gpt_analysis import render_analysis_section
from charts import render_price_section, render_indicator_table

# ========== CONFIGURAÇÕES ==========
st.set_page_config(page_title="Painel BTC/USDT", layout="wide")
set_custom_styles()

st.title("📈 Painel Bitget - Futuros BTC/USDT")

# ========== COLETA E CÁLCULOS ==========
df_1h = compute_indicators(fetch_and_process_candles("1H"))
df_4h = compute_indicators(fetch_and_process_candles("4H"))
df_1d = compute_indicators(fetch_and_process_candles("1D"))

if df_1h is not None and df_4h is not None and df_1d is not None:
    # Extração de info visual
    i1h, i4h, i1d = extract_info(df_1h), extract_info(df_4h), extract_info(df_1d)
    last_price = df_1h["close"].iloc[-1]
    var_pct = ((last_price - df_1h["close"].iloc[-2]) / df_1h["close"].iloc[-2]) * 100
    var_icon = "🔼" if var_pct > 0 else "🔽" if var_pct < 0 else "➖"
    var_class = "var-up" if var_pct > 0 else "var-down" if var_pct < 0 else "var-neutral"

    # ========== BLOCO SUPERIOR: Preço + Análise ==========
    col1, col2 = st.columns([1.2, 3])
    render_price_section(col1, last_price, var_pct, var_icon, var_class)
    render_analysis_section(col2, df_1h, df_4h, df_1d)

    # ========== TABELA DE INDICADORES ==========
    render_indicator_table(i1d, i4h, i1h)

else:
    st.error("❌ Erro ao carregar dados da API Bitget.")
