from datetime import datetime
import openai

# === Gera um bloco de indicadores para o prompt, formatado por timeframe
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

# === Gera a análise técnica com base nos dados de 3 timeframes
def gerar_analise_tecnica(df_1h, df_4h, df_1d):
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

    return response.choices[0].message.content
