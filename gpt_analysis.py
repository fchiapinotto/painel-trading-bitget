import streamlit as st
from datetime import datetime
import openai

# === Chave da API
openai.api_key = st.secrets["openai"]["openai_api_key"]

def render_analysis_section(container, df_1h, df_4h, df_1d):
    colA, colB, colC = container.columns([7, 1, 3])
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

    if "cached_analysis" not in st.session_state or (datetime.now() - st.session_state["last_update"]).seconds > 900:

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
            golden_cross = "Golden Cross" if sma50 > sma200 else "Death Cross"
            suporte = df["low"].min()
            resistencia = df["high"].max()
            preco = last["close"]
            variacao = ((last["close"] - df.iloc[-2]["close"]) / df.iloc[-2]["close"]) * 100

            return f"""
🔹 {label}:
- Preço: ${preco:,.0f}
- Variação: {variacao:.2f}%
- MACD: {macd:.2f} | Sinal: {signal:.2f}
- RSI: {rsi:.1f}
- Bollinger: ${lower:,.0f} – ${upper:,.0f}
- ADX: {adx:.1f}
- SMA 50: ${sma50:,.0f} | SMA 200: ${sma200:,.0f} ({golden_cross})
- Suporte: ${suporte:,.0f} | Resistência: ${resistencia:,.0f}
"""

        prompt = f"""
Você é um analista técnico de criptomoedas. Com base nas informações abaixo para os timeframes 1H, 4H e 1D, forneça uma análise clara, objetiva e embasada. A resposta deve conter:

1. **Momentum**: atrativo / neutro / adverso — com justificativa técnica.
2. **Tendência**: subida / descida / lateralizada — baseada em MACD, BB e SMA.
3. **Confiança**: alto / médio / baixo — considerando ADX, consistência entre os timeframes e clareza de sinais.

Evite repetições numéricas. Foque em interpretação e leitura técnica para orientar decisões de investimento.

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
            max_tokens=800
        )
        st.session_state["cached_analysis"] = response.choices[0].message.content

    st.markdown(f"""
    <div style='background:#f4f4f4;padding:15px;border-radius:8px; font-size:16px; line-height:1.6em;'>
        {st.session_state["cached_analysis"]}
        <br><br>
        <span style='font-size:12px;color:gray;'>🕒 Última atualização: {st.session_state["last_update"].strftime('%d/%m/%Y %H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)
