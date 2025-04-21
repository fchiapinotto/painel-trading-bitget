import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime
import openai

# === Chave OpenAI
openai.api_key = st.secrets["openai"]["openai_api_key"]

# === Config página
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

st.title("📈 Painel Bitget - Futuros BTC/USDT")
st.caption(f"🕒 Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} (GMT-3)")

# === Coleta de candles
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

# === Indicadores
def compute_indicators(df):
    df["ma20"] = df["close"].rolling(20).mean()
    df["std"] = df["close"].rolling(20).std()
    df["upper"] = df["ma20"] + 2 * df["std"]
    df["lower"] = df["ma20"] - 2 * df["std"]
    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()
    df["macd"] = ema12 - ema26
    df["signal"] = df["macd"].ewm(span=9).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))
    df["sma50"] = df["close"].rolling(50).mean()
    df["sma200"] = df["close"].rolling(200).mean()
    df["golden_cross"] = df["sma50"] > df["sma200"]
    high, low, close = df["high"], df["low"], df["close"]
    plus_dm = high.diff()
    minus_dm = low.diff()
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(14).mean() / atr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df["adx"] = dx.rolling(14).mean()
    return df

# === Dados e indicadores
df_1h = compute_indicators(fetch_and_process_candles("1H"))
df_4h = compute_indicators(fetch_and_process_candles("4H"))
df_1d = compute_indicators(fetch_and_process_candles("1D"))

# === Função resumo
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
    bb_icon = "🟦" if last["close"] > last["upper"] else "🟥" if last["close"] < last["lower"] else "🟨"
    bb_range = f"{last['lower']:,.0f} – {last['upper']:,.0f}"
    adx_icon = "🔥" if last["adx"] > 25 else "💤"
    sma_icon = "💰 Crz. Alta" if last["golden_cross"] else "💀 Crz. Baixa"
    support = df["low"].min()
    resistance = df["high"].max()
    sr_icon = "🧱" if last["close"] <= support else "🪟" if last["close"] >= resistance else "〰️"
    return (
        f"{trend_icon} <span class='{trend_class}'>{var:.2f}%</span>",
        f"{macd_icon} {macd_val:.2f}",
        f"{rsi_icon} {rsi_val:.1f}",
        f"{bb_icon} {bb_range}",
        f"{adx_icon} {last['adx']:.1f}",
        sma_icon,
        sr_icon
    )

if df_1h is not None:
    i1d, i4h, i1h = extract_info(df_1d), extract_info(df_4h), extract_info(df_1h)
    last_price = df_1h["close"].iloc[-1]
    var_pct = ((last_price - df_1h["close"].iloc[-2]) / df_1h["close"].iloc[-2]) * 100
    var_icon = "🔼" if var_pct > 0 else "🔽" if var_pct < 0 else "➖"
    var_class = "var-up" if var_pct > 0 else "var-down" if var_pct < 0 else "var-neutral"

col1, col2 = st.columns([1.2, 2.8])

with col1:
    st.markdown("<div class='titulo-secao'>💰 BTC Agora</div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='card-btc'>
            <div class='card-preco'>${last_price:,.0f}</div>
            <div class='card-var {var_class}'>{var_icon} {var_pct:.2f}%</div>
        </div>
        <div style='text-align:right; font-size:12px; color:gray;'>🕒 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(
        "<div style='display:flex;justify-content:space-between;align-items:center;'>"
        "<div class='titulo-secao'>🧠 Análise Técnica</div>"
        "<div>"
        + st.button("🔄", key="update_btn", help="Atualizar análise agora", use_container_width=False)
        + "</div></div>", unsafe_allow_html=True)

    if "last_update" not in st.session_state:
        st.session_state["last_update"] = datetime.now()

    if st.session_state.get("update_btn"):
        st.session_state["last_update"] = datetime.now()

    if "cached_analysis" not in st.session_state or (datetime.now() - st.session_state["last_update"]).seconds > 900:
        analysis_prompt = f"""
Você é um analista técnico. Com base nos indicadores MACD, RSI, Bollinger, ADX, SMA, Suporte e Resistência nos timeframes 1H, 4H, 1D, forneça uma análise técnica **resumida em até 450 caracteres**, estruturada em 3 classificações:

1. **Momentum**: atrativo / neutro / adverso – com breve justificativa técnica.
2. **Tendência**: subida / descida / lateralizada – com base em MACD, BB, SMA.
3. **Confiança**: alto / médio / baixo – considere volume, ADX e consistência entre timeframes.

Evite repetir números. Foque na **leitura técnica do cenário** atual.
        """
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um analista técnico objetivo, com tom profissional e direto."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.4,
            max_tokens=600
        )
        st.session_state["cached_analysis"] = response.choices[0].message.content

    st.markdown(f"""
    <div style='background:#f4f4f4;padding:15px;border-radius:8px; font-size:16px; line-height:1.6em;'>
        {st.session_state["cached_analysis"]}
        <br><span style='font-size:12px; color:gray;'>🕒 Última atualização: {st.session_state["last_update"].strftime('%d/%m/%Y %H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)
    

    # === Tabela técnica
    st.markdown("<div class='titulo-secao'>📊 Indicadores Técnicos</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <table>
        <tr>
            <th>Timeframe</th>
            <th title="Variação % preço">Variação</th>
            <th title="MACD vs linha de sinal">MACD</th>
            <th title="Força relativa (RSI)">RSI</th>
            <th title="Bandas de Bollinger">Bollinger</th>
            <th title="Tendência (ADX)">ADX</th>
            <th title="Médias 50/200 períodos">SMA</th>
            <th title="Suporte/Resistência">S/R</th>
        </tr>
        <tr><td>1D</td><td>{i1d[0]}</td><td>{i1d[1]}</td><td>{i1d[2]}</td><td>{i1d[3]}</td><td>{i1d[4]}</td><td>{i1d[5]}</td><td>{i1d[6]}</td></tr>
        <tr><td>4H</td><td>{i4h[0]}</td><td>{i4h[1]}</td><td>{i4h[2]}</td><td>{i4h[3]}</td><td>{i4h[4]}</td><td>{i4h[5]}</td><td>{i4h[6]}</td></tr>
        <tr><td>1H</td><td>{i1h[0]}</td><td>{i1h[1]}</td><td>{i1h[2]}</td><td>{i1h[3]}</td><td>{i1h[4]}</td><td>{i1h[5]}</td><td>{i1h[6]}</td></tr>
    </table>
    """, unsafe_allow_html=True)

    # === Legenda
    st.markdown("""
    <div style='margin-top:20px;font-size:15px'>
    <b>🔎 Legenda:</b><br>
    🔼/🔽: Tendência | 📈/📉/⏸️: MACD | 🟢/🟡/🔴: RSI | 🟦/🟥/🟨: Bollinger | 🔥/💤: ADX | 💰/💀: SMA | 🧱/🪟/〰️: Suporte/Resistência
    </div>
    """, unsafe_allow_html=True)
else:
    st.error("❌ Erro ao carregar dados da API Bitget.")
