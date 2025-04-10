import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Painel BTC/USDT", layout="wide")

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
        font-weight: bold;
        margin-bottom: 10px;
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
    th {
        background-color: #f0f0f0;
        header-align: center;
        text-align: center;
        padding: 10px;
    }
    td {
        text-align: center;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Painel Bitget - Futuros BTC/USDT")
st.caption(f"🕒 Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} (GMT-3)")

# === Função para buscar e processar candles ===
def fetch_and_process_candles(granularity="1H", limit=100):
    url = "https://api.bitget.com/api/v2/mix/market/candles"
    params = {
        "symbol": "BTCUSDT",
        "productType": "USDT-FUTURES",
        "granularity": granularity,
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data["code"] != "00000":
        return None

    df = pd.DataFrame(data["data"], columns=["timestamp", "open", "high", "low", "close", "volume", "quote_volume"])
    df = df.astype({"timestamp": "int64", "open": "float", "high": "float", "low": "float", "close": "float"})
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.tz_convert("America/Sao_Paulo")
    df.sort_values("timestamp", inplace=True)
    return df

# === Função para calcular indicadores técnicos ===
def compute_indicators(df):
    df["ma20"] = df["close"].rolling(window=20).mean()
    df["std"] = df["close"].rolling(window=20).std()
    df["upper"] = df["ma20"] + 2 * df["std"]
    df["lower"] = df["ma20"] - 2 * df["std"]

    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    return df

# === Consultar dados ===
df_1h = compute_indicators(fetch_and_process_candles("1H", 100))
df_4h = compute_indicators(fetch_and_process_candles("4H", 100))
df_1d = compute_indicators(fetch_and_process_candles("1D", 100))

if df_1h is not None and df_4h is not None and df_1d is not None:

    def extract_info(df):
        last = df.iloc[-1]
        prev = df.iloc[-2]
        var = ((last["close"] - prev["close"]) / prev["close"]) * 100
        trend_icon = "🔼" if var > 0 else "🔽" if var < 0 else "➖"
        trend_class = "var-up" if var > 0 else "var-down" if var < 0 else "var-neutral"
        macd_val = last["macd"] - last["signal"]
        macd_icon = "📈" if macd_val > 0 else "📉" if macd_val < 0 else "⏸️"
        rsi_val = last["rsi"]
        rsi_icon = "🟢" if rsi_val > 70 else "🔴" if rsi_val < 30 else "🟡"
        bb_range = f"{last['lower']:,.0f} – {last['upper']:,.0f}"
        return (
            f"{trend_icon} <span class='{trend_class}'>{var:.2f}%</span>",
            f"{macd_icon} {macd_val:.2f}",
            f"{rsi_icon} {rsi_val:.1f}",
            bb_range
        )

    v1d, m1d, r1d, b1d = extract_info(df_1d)
    v4h, m4h, r4h, b4h = extract_info(df_4h)
    v1h, m1h, r1h, b1h = extract_info(df_1h)

    # BLOCO SUPERIOR
    last_price = df_1h["close"].iloc[-1]
    prev_price = df_1h["close"].iloc[-2]
    var_pct = ((last_price - prev_price) / prev_price) * 100
    var_class = "var-up" if var_pct > 0 else "var-down" if var_pct < 0 else "var-neutral"
    var_icon = "🔼" if var_pct > 0 else "🔽" if var_pct < 0 else "➖"

    colA, colB = st.columns([0.8 , 2])

    with colA:
        st.markdown("<div class='titulo-secao'>💰 BTC Agora</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='card-btc'>
            <div class='card-preco'>${last_price:,.0f}</div>
            <div class='card-var {var_class}'>{var_icon} {var_pct:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown("<div class='titulo-secao'>📊 Indicadores Técnicos</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <table>
        <tr><th>Timeframe</th><th>Variação %</th><th>MACD</th><th>RSI</th><th>Bollinger</th></tr>
        <tr><td>1D</td><td>{v1d}</td><td>{m1d}</td><td>{r1d}</td><td>{b1d}</td></tr>
        <tr><td>4H</td><td>{v4h}</td><td>{m4h}</td><td>{r4h}</td><td>{b4h}</td></tr>
        <tr><td>1H</td><td>{v1h}</td><td>{m1h}</td><td>{r1h}</td><td>{b1h}</td></tr>
        </table>
        """, unsafe_allow_html=True)

    # GRÁFICO DE 1H
    df_48h = df_1h[-48:]
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df_48h["timestamp"],
        open=df_48h["open"],
        high=df_48h["high"],
        low=df_48h["low"],
        close=df_48h["close"],
        name="Candles"
    ))

    fig.add_trace(go.Scatter(x=df_48h["timestamp"], y=df_48h["upper"], mode="lines", name="BB Superior",
                             line=dict(color="blue", dash="dot")))
    fig.add_trace(go.Scatter(x=df_48h["timestamp"], y=df_48h["ma20"], mode="lines", name="BB Média",
                             line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=df_48h["timestamp"], y=df_48h["lower"], mode="lines", name="BB Inferior",
                             line=dict(color="red", dash="dot")))

    fig.update_layout(
        title="<b>📉 BTC/USDT - Últimas 48 horas</b>",
        title_font_size=24,
        xaxis_title="Horário",
        yaxis_title="Preço",
        xaxis=dict(tickformat="%d/%m %Hh"),
        hovermode="x unified",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("❌ Erro ao carregar dados da API Bitget.")
