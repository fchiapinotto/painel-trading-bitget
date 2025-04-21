import streamlit as st

def aplicar_estilos():
    st.markdown("""
        <style>
        .titulo-secao {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
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
