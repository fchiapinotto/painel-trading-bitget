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

st.title("📈 Painel Bitget - Futuros BTC/USDT")
# === Consulta candles
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

# Coleta e cálculo dos dados
df_1h = compute_indicators(fetch_and_process_candles("1H"))
df_4h = compute_indicators(fetch_and_process_candles("4H"))
df_1d = compute_indicators(fetch_and_process_candles("1D"))
# === Função resumo com ícones e dados
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
    sr_icon = f"🧱 {support:,.0f}<br>🪟 {resistance:,.0f}"
    return (
        f"{trend_icon} <span class='{trend_class}'>{var:.2f}%</span>",
        f"{macd_icon} {macd_val:.2f}",
        f"{rsi_icon} {rsi_val:.1f}",
        f"{bb_icon} {bb_range}",
        f"{adx_icon} {last['adx']:.1f}",
        sma_icon,
        sr_icon
    )

# === Cálculo e estruturação dos dados
if df_1h is not None:
    i1d, i4h, i1h = extract_info(df_1d), extract_info(df_4h), extract_info(df_1h)
    last_price = df_1h["close"].iloc[-1]
    var_pct = ((last_price - df_1h["close"].iloc[-2]) / df_1h["close"].iloc[-2]) * 100
    var_icon = "🔼" if var_pct > 0 else "🔽" if var_pct < 0 else "➖"
    var_class = "var-up" if var_pct > 0 else "var-down" if var_pct < 0 else "var-neutral"

    # === Topo com preço e análise
    col1, col2 = st.columns([1.2, 3])
    with col1:
        st.markdown("<div class='titulo-secao'>💰 BTC Agora</div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='card-btc'>
                <div class='card-preco'>${last_price:,.0f}</div>
                <div class='card-var {var_class}'>{var_icon} {var_pct:.2f}%</div>
            </div>
            <div style='text-align:right; font-size:12px; color:gray;'>🕒 Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
        """, unsafe_allow_html=True)

    with col2:
        colA, colB, colC = st.columns([7, 1, 3])
        with colA:
            st.markdown("<div class='titulo-secao'>🧠 Análise Técnica</div>", unsafe_allow_html=True)
        with colB:
            refresh = st.button("🔄", help="Atualizar análise")
        with colC:
            st.markdown(f"<div style='text-align:right; font-size:12px; color:gray;'>🕒 Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>", unsafe_allow_html=True)

        if "last_update" not in st.session_state:
            st.session_state["last_update"] = datetime.now()

        if refresh:
            st.session_state["last_update"] = datetime.now()

               if "cached_analysis" not in st.session_state or (
            datetime.now() - st.session_state["last_update"]).seconds > 900:

            def build_block(df, label):
                last = df.iloc[-1]
                macd = last["macd"]
                signal = last["signal"]
                rsi = last["rsi"]
                upper = last["upper"]
                lower = last["lower"]
                adx = last["adx"]
                sma50 = last["sma50"]
                sma200 = last["sma200"]
                suporte = df["low"].min()
                resistencia = df["high"].max()
                preco = last["close"]
                variacao = ((last["close"] - df.iloc[-2]["close"]) / df.iloc[-2]["close"]) * 100

                return f"""
🔹 {label}:
- Preço atual: ${preco:,.0f}
- Variação: {variacao:.2f}%
- MACD: {macd:.2f} | Sinal: {signal:.2f}
- RSI: {rsi:.1f}
- Bollinger: Limites [${lower:,.0f} – ${upper:,.0f}]
- ADX: {adx:.1f}
- SMA 50: {sma50:,.0f} | SMA 200: {sma200:,.0f}
- Suporte: ${suporte:,.0f} | Resistência: ${resistencia:,.0f}
"""

            prompt = f"""
Você é um analista técnico. Com base nos indicadores abaixo, forneça uma análise **resumida e clara** com foco em ajudar um investidor a entender se o momento atual oferece oportunidade ou exige cautela. Estruture sua resposta com 3 classificações:

1. **Momentum**: atrativo / neutro / adverso – e sua leitura.
2. **Tendência**: subida / descida / lateralizada – com justificativa técnica.
3. **Confiança**: alto / médio / baixo – com base em ADX, volume e convergência dos timeframes.

A análise deve ser objetiva, profissional e embasada tecnicamente.

Indicadores:
{build_block(df_1h, "1H")}
{build_block(df_4h, "4H")}
{build_block(df_1d, "1D")}
"""

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um analista técnico profissional e direto."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=700
            )
            st.session_state["cached_analysis"] = response.choices[0].message.content

        st.markdown(f"""
        <div style='background:#f4f4f4;padding:15px;border-radius:8px; font-size:16px; line-height:1.6em;'>
            {st.session_state["cached_analysis"]}
        </div>
        """, unsafe_allow_html=True)

    # === Tabela técnica
    st.markdown("<div class='titulo-secao'>📊 Indicadores Técnicos</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <table>
        <tr>
            <th>Timeframe</th>
            <th title="Variação percentual do preço em relação ao candle anterior.">Variação</th>
            <th title="Diferença entre MACD e sua média de sinal.">MACD</th>
            <th title="Índice de Força Relativa, indica sobrecompra/sobrevenda.">RSI</th>
            <th title="Bandas de Bollinger — volatilidade e extremos de preço.">Bollinger</th>
            <th title="ADX mostra força da tendência, acima de 25 indica força.">ADX</th>
            <th title="Golden/Death Cross: média móvel 50 vs 200.">SMA</th>
            <th title="Níveis extremos recentes de preço (suporte/resistência).">S/R</th>
        </tr>
        <tr><td>1D</td><td>{i1d[0]}</td><td>{i1d[1]}</td><td>{i1d[2]}</td><td>{i1d[3]}</td><td>{i1d[4]}</td><td>{i1d[5]}</td><td>{i1d[6]}</td></tr>
        <tr><td>4H</td><td>{i4h[0]}</td><td>{i4h[1]}</td><td>{i4h[2]}</td><td>{i4h[3]}</td><td>{i4h[4]}</td><td>{i4h[5]}</td><td>{i4h[6]}</td></tr>
        <tr><td>1H</td><td>{i1h[0]}</td><td>{i1h[1]}</td><td>{i1h[2]}</td><td>{i1h[3]}</td><td>{i1h[4]}</td><td>{i1h[5]}</td><td>{i1h[6]}</td></tr>
    </table>
    """, unsafe_allow_html=True)

    # === Legenda expandida
    st.markdown("""
    <div style='margin-top:20px; font-size:15px'>
    <b>🔎 Legenda de Indicadores e Ícones:</b><br>
    🔼/🔽: Variação positiva/negativa no último candle.  
    📈/📉/⏸️: MACD maior/menor/igual ao sinal – tendência crescente, decrescente ou neutra.  
    🟢 RSI &gt; 70 (sobrecompra) | 🔴 RSI &lt; 30 (sobrevenda) | 🟡 zona neutra (30–70).  
    🟦 Preço acima da banda superior | 🟥 abaixo da inferior | 🟨 dentro das bandas.  
    🔥 ADX &gt; 25 (tendência forte) | 💤 tendência fraca ou lateral.  
    💰 Crz. Alta (SMA50 cruzando acima da SMA200) | 💀 Crz. Baixa (SMA50 abaixo da SMA200).  
    🧱 Suporte | 🪟 Resistência — baseados nos extremos de preço recentes | 〰️ entre zonas.
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("❌ Erro ao carregar dados da API Bitget.")
