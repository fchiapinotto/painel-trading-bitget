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

    sma_icon = "💰 Crz. Alta" if last["sma50"] > last["sma200"] else "💀 Crz. Baixa"

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
