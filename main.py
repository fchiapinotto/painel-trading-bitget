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

# === COLETA DOS 3 TIMEFRAMES ===
df_1h = fetch_and_process_candles("1H")
df_4h = fetch_and_process_candles("4H")
df_1d = fetch_and_process_candles("1D")


if df_1h is not None and df_4h is not None and df_1d is not None:
    # === CÁLCULO DE INDICADORES TÉCNICOS ===
    df_1h = compute_indicators(df_1h)
    df_4h = compute_indicators(df_4h)
    df_1d = compute_indicators(df_1d)

    # === EXTRAÇÃO DE SÍMBOLOS E ÍCONES ===
    i1h = extract_info(df_1h)
    i4h = extract_info(df_4h)
    i1d = extract_info(df_1d)

    last_price = df_1h["close"].iloc[-1]
    


    # ========== BLOCO SUPERIOR: Preço + Análise ==========
    col1, col2 = st.columns([1.2, 3])
    render_price_section(col1, last_price, var_pct, var_icon, var_class)
    render_analysis_section(col2, df_1h, df_4h, df_1d)

    # ========== TABELA DE INDICADORES ==========
    render_indicator_table(i1d, i4h, i1h)

else:
    st.error("❌ Erro ao carregar dados da API Bitget.")
