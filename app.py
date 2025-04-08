# app_btc_analise_tecnica.py
import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
import plotly.graph_objects as go
from scipy.signal import argrelextrema

# ========== 🧠 GPT ANALYSIS PLACEHOLDER ==========
def generate_gpt_analysis(df, timeframe):
    last_rsi = df['RSI'].iloc[-1]
    last_macd = df['MACD'].iloc[-1]
    signal = df['Signal'].iloc[-1]
    bb_width = (df['BB_Upper'] - df['BB_Lower']).iloc[-1]

    if last_rsi < 30:
        trend = "possível sobrevenda"
    elif last_rsi > 70:
        trend = "possível sobrecompra"
    elif last_macd > signal:
        trend = "momentum positivo"
    else:
        trend = "lateralização ou correção"

    return f"{timeframe}: {trend}, RSI em {last_rsi:.1f}, MACD {'acima' if last_macd > signal else 'abaixo'} do sinal."

# ========== 🧮 INDICADORES ==========
def compute_indicators(df):
    df["EMA12"] = df["close"].ewm(span=12).mean()
    df["EMA26"] = df["close"].ewm(span=26).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["Signal"] = df["MACD"].ewm(span=9).mean()
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    df["BB_Mid"] = df["close"].rolling(20).mean()
    df["BB_Upper"] = df["BB_Mid"] + 2 * df["close"].rolling(20).std()
    df["BB_Lower"] = df["BB_Mid"] - 2 * df["close"].rolling(20).std()
    return df

# ========== 🔻 SUPORTES ==========
def detect_supports(df, order=10):
    lows = df["low"].values
    indices = argrelextrema(lows, np.less_equal, order=order)[0]
    return df.iloc[indices][["low"]]

# ========== 🔄 API BITGET ==========
def get_candles(symbol="BTCUSDT", granularity="1h", limit=200):
    url = f"https://api.bitget.com/api/mix/v1/market/candles"
    params = {"symbol": symbol, "granularity": granularity, "limit": limit, "productType": "umcbl"}
    r = requests.get(url, params=params)
    data = r.json()["data"]
    df = pd.DataFrame(data, columns=["timestamp","open","high","low","close","volume","turnover"])
    df = df.astype(float)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df = df.sort_values("timestamp")
    df.set_index("timestamp", inplace=True)
    return df

# ========== 📊 TELA ==========
st.set_page_config("Painel BTC/USDT", layout="wide")
st.title("📊 BTC/USDT – Visão Técnica Avançada")
st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Consulta e indicadores
timeframes = {"1D": "1440", "4H": "240", "1H": "60"}
data = {}
support_levels = {}

for tf_label, tf_val in timeframes.items():
    df = get_candles("BTCUSDT", tf_val)
    df = compute_indicators(df)
    supports = detect_supports(df)
    data[tf_label] = df
    support_levels[tf_label] = supports

# Valor atual
price_now = data["1H"]["close"].iloc[-1]
st.subheader(f"💰 Preço Atual BTC/USDT: ${price_now:,.2f}")

# Tabela de indicadores por timeframe
st.markdown("### 📊 Indicadores Técnicos (Resumo)")
table = []
for tf, df in data.items():
    delta = df["close"].iloc[-1] - df["close"].iloc[-2]
    perc = (delta / df["close"].iloc[-2]) * 100
    table.append({
        "Timeframe": tf,
        "Variação": f"{perc:+.2f}%" + (" 🔺" if perc > 0 else " 🔻"),
        "MACD": f"{df['MACD'].iloc[-1]:.2f}",
        "RSI": f"{df['RSI'].iloc[-1]:.1f}",
        "Bollinger": f"{df['BB_Upper'].iloc[-1]:.0f} / {df['BB_Lower'].iloc[-1]:.0f}",
        "Análise GPT": generate_gpt_analysis(df, tf)
    })
st.dataframe(pd.DataFrame(table))

# Plot do gráfico interativo com plotly
df_plot = data["1H"]
fig = go.Figure(data=[
    go.Candlestick(x=df_plot.index, open=df_plot["open"], high=df_plot["high"],
                   low=df_plot["low"], close=df_plot["close"], name="Candles"),
    go.Scatter(x=df_plot.index, y=df_plot["BB_Upper"], mode='lines', name='BB Upper', line=dict(color='gray')),
    go.Scatter(x=df_plot.index, y=df_plot["BB_Lower"], mode='lines', name='BB Lower', line=dict(color='gray')),
])
for level in support_levels["1H"]["low"]:
    fig.add_hline(y=level, line_dash="dot", line_color="green")
fig.update_layout(title="📈 Gráfico BTC/USDT (1H)", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# Estratégia sugerida
st.markdown("### 📌 Estratégias Recomendadas (Grid Trading)")
grid_table = pd.DataFrame([
    {"Modo": "Long", "Estratégia": "Pullback suporte", "Favorável": "✅", "Trigger": "Aprox. 81K",
     "Faixa": "81K–84K", "Grades": 8, "Alav.": "3x", "Trailing": "Sim", "SL/TP": "SL 79K / TP 88K", "Duração": "3–5d"},
    {"Modo": "Short", "Estratégia": "Reteste resistência", "Favorável": "❌", "Trigger": "Break 86K",
     "Faixa": "85K–87K", "Grades": 10, "Alav.": "4x", "Trailing": "Não", "SL/TP": "SL 88K / TP 82K", "Duração": "2–4d"},
    {"Modo": "Neutro", "Estratégia": "Lateralidade confirmada", "Favorável": "✅", "Trigger": "Range ativo",
     "Faixa": "82K–85K", "Grades": 12, "Alav.": "2x", "Trailing": "Sim", "SL/TP": "SL 81 / TP 86", "Duração": "1–3d"},
])
st.dataframe(grid_table)
