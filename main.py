import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from styles import set_custom_styles
from fetch_data import fetch_and_process_candles
from indicators import compute_indicators, extract_supports_resistances
from extract_info import extract_info
from charts import render_candles_bollinger
from gpt_analysis import gpt_events, gpt_highlight, gpt_grid_scenarios

# --- AUTO-REFRESH ---
# Atualiza dados e gráficos a cada 1 minuto
st_autorefresh(interval=60_000, key="data_refresher")
# Força atualização dos prompts GPT a cada 15 min via ttl no cache

# CONFIGURAÇÕES VISUAIS
set_custom_styles()  # aplica tema light
st.set_page_config(layout="wide", page_title="Painel Bitget BTC/USDT")

# ---- 1) TOPO: RESUMO ÚNICO + BADGES ----
# Coleta e processa candles 1H
df_1h = fetch_and_process_candles("1H")
df_1h = compute_indicators(df_1h)
info = extract_info(df_1h)

last_price = df_1h["close"].iloc[-1]
prev_price = df_1h["close"].iloc[-2]
var_pct = (last_price - prev_price) / prev_price * 100

# Badges
sentimento = info.get("sentimento", "Neutro")
tendencia = info.get("tendencia", "Neutra")
forca = info.get("forca_tendencia", 3)

with st.container():
    st.markdown("## 📈 BTC/USDT")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric("Preço Atual (USDT)", f"{last_price:,.2f}", f"{var_pct:.2f}%")
    with col2:
        st.markdown(f"**Sentimento:** {sentimento}")
        st.markdown(f"**Tendência:** {tendencia}")
        st.markdown(f"**Força (1–5):** {forca}")

# ---- 2) MIOLO: 2 COLUNAS PRINCIPAIS ----
colL, colR = st.columns([2, 1])

with colL:
    # Gráfico com BB e suportes/topos (últimas 24h)
    sr = extract_supports_resistances(df_1h, period="24H")
    render_candles_bollinger(df_1h, support_resistance=sr)

with colR:
    # GPT Highlight (modelo o3)
    highlight = gpt_highlight(df_1h, info)
    st.markdown("### 🤖 Insight Rápido")
    st.write(highlight["sentenca"])
    for b in highlight["bullets"]:
        st.write(f"- {b}")

    # Alertas de Grid Trading
    alerts = gpt_grid_scenarios(df_1h, info)
    st.markdown("### 🚨 Alertas de Grid")
    st.table(pd.DataFrame(alerts))

# ---- 3) TABELA DE INDICADORES FULL WIDTH ----
st.markdown("### 📊 Indicadores Técnicos")
ind_df = pd.DataFrame({
    "Indicador": ["MACD", "RSI", "BB Width", "ADX"],
    "1H": [info.get('macd'), info.get('rsi'), info.get('bb_width'), info.get('adx')],
    "4H": [info.get('macd_4h'), info.get('rsi_4h'), info.get('bb_width_4h'), info.get('adx_4h')],
    "1D": [info.get('macd_1d'), info.get('rsi_1d'), info.get('bb_width_1d'), info.get('adx_1d')]
})
st.table(ind_df.set_index("Indicador"))
st.caption("Legenda: RSI>70→Sobrecomprado; MACD>0→Alta; BBWidth↑→Volatilidade alta")

# ---- 4) CENÁRIOS DE GRID (GPT O3) ----
st.markdown("## 📋 Cenários de Grid Trading")
scenarios = gpt_grid_scenarios(df_1h, info, events=gpt_events())
cols = st.columns(3)
for col, sc in zip(cols, scenarios):
    with col:
        st.markdown(f"### {sc['tipo']}")
        for k, v in sc.items():
            if k != 'tipo':
                st.markdown(f"**{k.capitalize()}:** {v}")

# ---- 5) EVENTOS RELEVANTES (GPT O3) ----
st.markdown("### 🗓️ Eventos Relevantes")
events = gpt_events()
for e in events:
    st.write(f"- {e['date']} — {e['title']}")
