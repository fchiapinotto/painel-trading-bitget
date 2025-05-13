import streamlit as st

def set_custom_styles():
    st.markdown("""
    <style>
    body { background-color: #ffffff; color: #333333; }
    .stMetric > div { font-size: 2em; }
    .titulo-secao { font-weight: bold; margin-top: 1rem; }
    .badge { background: #1f4e78; color: #ffffff; padding: 4px 8px; border-radius: 4px; margin-right: 4px; }
    </style>
    """, unsafe_allow_html=True)
