import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime
import openai

# === Carregar chave da OpenAI do secrets
openai.api_key = st.secrets["openai"]["openai_api_key"]

# === Configuração da página
st.set_page_config(page_title="Painel BTC/USDT", layout="wide")

# === Estilos
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
        margin-bottom: 25px;
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

# === Consulta candles e indicadores
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
    df = df.astype({"timestamp": "int64", "open": "float", "high": "float", "low": "float", "close": "float", "volume": "float"})
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.tz_convert("America/Sao_Paulo")
    df.sort_values("timestamp", inplace=True)
    return df

# === Indicadores Técnicos
def compute_indicators(df):
    df["ma20"] = df["close"].rolling(window=20).mean()
    df["std"] = df["close"].rolling(window=20).std()
    df["upper"] = df["ma20"] + 2 * df["std"]
    df["lower"] = df["ma20"] - 2 * df["std"]

    # MACD
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    # RSI
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # SMA 50/200
    df["sma50"] = df["close"].rolling(window=50).mean()
    df["sma200"] = df["close"].rolling(window=200).mean()
    df["golden_cross"] = (df["sma50"] > df["sma200"])

    # ADX
    high = df["high"]
    low = df["low"]
    close = df["close"]
    plus_dm = high.diff()
    minus_dm = low.diff()
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(14).mean() / atr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df["adx"] = dx.rolling(14).mean()

    return df

# Coleta e cálculo dos dados
df_1h = compute_indicators(fetch_and_process_candles("1H"))
df_4h = compute_indicators(fetch_and_process_candles("4H"))
df_1d = compute_indicators(fetch_and_process_candles("1D"))

# Função resumo com ícones e legendas
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
    bb = f"{last['lower']:,.0f} – {last['upper']:,.0f}"
    bb_icon = "🟦" if last["close"] > last["upper"] else "🟥" if last["close"] < last["lower"] else "🟨"
    cross_icon = "💰 Crz. Alta" if last["golden_cross"] else "💀 Crz. Baixa"
    adx_icon = "🔥" if last["adx"] > 25 else "💤"
    volume_icon = f"{last['volume']:,.0f}"
    support = df["low"].min()
    resistance = df["high"].max()
    sr_icon = "🧱" if last["close"] <= support else "🪟" if last["close"] >= resistance else "〰️"
    return (
        f"{trend_icon} <span class='{trend_class}'>{var:.2f}%</span>",
        f"{macd_icon} {macd_val:.2f}",
        f"{rsi_icon} {rsi_val:.1f}",
        f"{bb_icon} {bb}",
        f"{adx_icon} {last['adx']:.1f}",
        f"{cross_icon}",
        sr_icon,
        volume_icon
    )

if df_1h is not None and df_4h is not None and df_1d is not None:
    # Coleta dados formatados
    i1d = extract_info(df_1d)
    i4h = extract_info(df_4h)
    i1h = extract_info(df_1h)

    last_price = df_1h["close"].iloc[-1]
    prev_price = df_1h["close"].iloc[-2]
    var_pct = ((last_price - prev_price) / prev_price) * 100
    var_class = "var-up" if var_pct > 0 else "var-down" if var_pct < 0 else "var-neutral"
    var_icon = "🔼" if var_pct > 0 else "🔽" if var_pct < 0 else "➖"

    # === Bloco Superior
    colA, colB = st.columns([0.8, 2])
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
        <tr><th>Timeframe</th><th>Variação</th><th>MACD</th><th>RSI</th><th>Bollinger</th><th>ADX</th><th>SMA 50/200</th><th>S/R</th><th>Volume</th></tr>
        <tr><td>1D</td><td>{i1d[0]}</td><td>{i1d[1]}</td><td>{i1d[2]}</td><td>{i1d[3]}</td><td>{i1d[4]}</td><td>{i1d[5]}</td><td>{i1d[6]}</td><td>{i1d[7]}</td></tr>
        <tr><td>4H</td><td>{i4h[0]}</td><td>{i4h[1]}</td><td>{i4h[2]}</td><td>{i4h[3]}</td><td>{i4h[4]}</td><td>{i4h[5]}</td><td>{i4h[6]}</td><td>{i4h[7]}</td></tr>
        <tr><td>1H</td><td>{i1h[0]}</td><td>{i1h[1]}</td><td>{i1h[2]}</td><td>{i1h[3]}</td><td>{i1h[4]}</td><td>{i1h[5]}</td><td>{i1h[6]}</td><td>{i1h[7]}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        st.markdown("""
        🔎 **Legenda de Ícones**  
        🔼/🔽: Tendência | 📈/📉: MACD | 🟢/🔴/🟡: RSI | 🟦/🟥: Bollinger |  
        💰 Crz. Alta / 💀 Crz. Baixa: SMA | 🔥 Forte ADX / 💤 Fraco |  
        🧱 Suporte / 🪟 Resistência / 〰️ Zona neutra
        """)

    # === Gráfico
    df_48h = df_1h[-48:]
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df_48h["timestamp"], open=df_48h["open"], high=df_48h["high"],
                                 low=df_48h["low"], close=df_48h["close"]))
    fig.add_trace(go.Scatter(x=df_48h["timestamp"], y=df_48h["upper"], mode="lines", name="BB Superior"))
    fig.add_trace(go.Scatter(x=df_48h["timestamp"], y=df_48h["ma20"], mode="lines", name="BB Média"))
    fig.add_trace(go.Scatter(x=df_48h["timestamp"], y=df_48h["lower"], mode="lines", name="BB Inferior"))
    fig.update_layout(
        title="<b>📉 BTC/USDT - Últimas 48 horas</b>",
        xaxis_title="Horário", yaxis_title="Preço",
        hovermode="x unified", height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # === Análise GPT
    st.markdown("<div class='titulo-secao'>📋 Análise de Especialista – Crypto Trade Analyst</div>", unsafe_allow_html=True)
    if st.button("🔍 Gerar Análise Técnica"):
        prompt = f"""
Você é um analista técnico especialista em futuros de criptomoedas. Sua missão é produzir uma análise objetiva, clara e profissional com base nos dados técnicos do par BTC/USDT, contemplando:

1. 🎯 **Tendência e sinais técnicos** — descreva a direção do mercado e comportamento atual com base nos indicadores (MACD, RSI, Bollinger Bands, Suporte, Resistência, Volume, Médias Móveis e ADX). Identifique se há força, fraqueza ou indecisão.

2. 🚀 **Oportunidades de Trading (foco em Grid e Breakout)** — destaque *até 2 oportunidades reais* com base nos dados apresentados. Informe a lógica técnica e os preços de referência (ex: zonas de entrada, rompimentos, retestes etc.).

3. ⚠️ **Riscos e Alertas Estratégicos** — elenque os principais riscos para entradas longas ou curtas. Alerte sobre condições como sobrecompra, falso rompimento, suporte fraco ou ausência de volume.

📌 Preço atual: ${last_price:,.0f}
        """
        with st.spinner("Gerando análise..."):
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um analista técnico de criptomoedas especialista em futuros. Seja direto, técnico e objetivo."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            st.success("✅ Análise gerada com sucesso!")
            st.markdown(f"<div style='background:#f9f9f9;padding:20px;border-radius:10px'>{response.choices[0].message.content}</div>", unsafe_allow_html=True)

else:
    st.error("❌ Erro ao carregar dados da API Bitget.")
