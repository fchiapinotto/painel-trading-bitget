import plotly.graph_objects as go
import streamlit as st

def render_price_chart(df, title="📉 BTC/USDT - Últimas 48 horas"):
    df_48h = df[-48:]  # últimas 48 horas

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df_48h["timestamp"],
        open=df_48h["open"],
        high=df_48h["high"],
        low=df_48h["low"],
        close=df_48h["close"],
        name="Candlestick"
    ))

    fig.add_trace(go.Scatter(
        x=df_48h["timestamp"],
        y=df_48h["upper"],
        mode="lines",
        name="BB Superior"
    ))

    fig.add_trace(go.Scatter(
        x=df_48h["timestamp"],
        y=df_48h["ma20"],
        mode="lines",
        name="BB Média"
    ))

    fig.add_trace(go.Scatter(
        x=df_48h["timestamp"],
        y=df_48h["lower"],
        mode="lines",
        name="BB Inferior"
    ))

    fig.update_layout(
        title=f"<b>{title}</b>",
        xaxis_title="Horário",
        yaxis_title="Preço",
        hovermode="x unified",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
