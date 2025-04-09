
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# Carregar os dados CSV
df = pd.read_csv("candles_btcusdt_1h.csv")  # ajuste para o caminho correto se necessário

# Processar dados
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)
df = df[['open', 'high', 'low', 'close']].astype(float)

# Indicadores técnicos
rsi = df['close'].diff().apply(lambda x: max(x, 0)).rolling(14).mean() / \
      df['close'].diff().abs().rolling(14).mean() * 100
macd_line = df['close'].ewm(span=12).mean() - df['close'].ewm(span=26).mean()
bb_middle = df['close'].rolling(20).mean()
bb_std = df['close'].rolling(20).std()
bb_upper = bb_middle + 2 * bb_std
bb_lower = bb_middle - 2 * bb_std

# Últimos valores
last_price = df['close'].iloc[-1]
prev_price = df['close'].iloc[-2]
price_change = ((last_price - prev_price) / prev_price) * 100
last_rsi = rsi.iloc[-1]
last_macd = macd_line.iloc[-1]
last_bb_upper = bb_upper.iloc[-1]
last_bb_lower = bb_lower.iloc[-1]

# Painel superior
st.set_page_config(layout="wide")
st.title("📊 Painel Bitget - Futuros BTC/USDT (1H)")
st.markdown(f"🕒 Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Preço Atual", f"${last_price:,.2f}")
col2.metric("Variação 1H", f"{price_change:+.2f}%")
col3.metric("RSI (14)", f"{last_rsi:.2f}")
col4.metric("MACD", f"{last_macd:.2f}")
col5.metric("Bollinger", f"{last_bb_lower:.2f} – {last_bb_upper:.2f}")

# Gráfico interativo
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close'],
    name="Candles"
))

fig.add_trace(go.Scatter(x=df.index, y=bb_upper, name='BB Superior',
                         line=dict(color='blue', dash='dot')))
fig.add_trace(go.Scatter(x=df.index, y=bb_middle, name='BB Média',
                         line=dict(color='blue')))
fig.add_trace(go.Scatter(x=df.index, y=bb_lower, name='BB Inferior',
                         line=dict(color='red', dash='dot')))

fig.update_layout(
    title="BTC/USDT (1H) com Bollinger Bands",
    xaxis_title="Data",
    yaxis_title="Preço",
    hovermode="x unified",
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)
