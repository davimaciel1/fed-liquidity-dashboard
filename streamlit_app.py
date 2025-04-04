# fed_liquidity_dashboard/streamlit_app.py

import streamlit as st
import pandas as pd
import requests
import yfinance as yf
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Painel de Liquidez do FED", layout="wide")
FRED_API_KEY = "57a975cb3b6c38b1344f6b85ebd760d2"  # Substitua pela sua chave da FRED
FRED_URL = f"https://api.stlouisfed.org/fred/series/observations?series_id=WALCL&api_key={FRED_API_KEY}&file_type=json"

# --- TÍTULO ---
st.title("📊 Painel de Liquidez do FED (WALCL)")

# --- COLETA WALCL ---
walcl_data = requests.get(FRED_URL).json()
dates = [obs["date"] for obs in walcl_data["observations"]]
values = [float(obs["value"]) if obs["value"] != "." else None for obs in walcl_data["observations"]]
df = pd.DataFrame({"Data": pd.to_datetime(dates), "WALCL": values}).dropna()
df.sort_values("Data", inplace=True)
df["Δ Semanal"] = df["WALCL"].diff()

# --- VALORES ATUAIS ---
last_val = df["WALCL"].iloc[-1]
last_val_trilhoes = last_val / 1_000_000
last_delta = df["Δ Semanal"].iloc[-1]
last_delta_bilhoes = last_delta / 1_000

# --- INTERPRETAÇÃO ---
if last_delta > 0:
    interp = f"🟩 Liquidez em expansão (+${last_delta_bilhoes:,.2f} bilhões)"
    insight = "🟢 O Fed está expandindo a liquidez. Potencial suporte ao mercado."
else:
    interp = f"🟥 Liquidez em contração (-${abs(last_delta_bilhoes):,.2f} bilhões)"
    insight = "🔴 O Fed está drenando liquidez. Pode pressionar ações e cripto."

# --- EXIBIÇÃO ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Último valor (WALCL)", f"${last_val_trilhoes:,.2f} Trilhões")
    st.metric("Δ Semanal", f"{last_delta_bilhoes:,.2f} Bilhões")
with col2:
    st.write("**🔍 Interpretação automática:**")
    st.info(interp)
    st.warning(insight)

st.line_chart(df.set_index("Data")["WALCL"])

# --- COMPARATIVO COM ATIVOS ---
st.subheader("📈 Comparativo com SP500, Nasdaq e BTC")

try:
    # Baixar dados
    spx_df = yf.download('^GSPC', period='6mo')
    nasdaq_df = yf.download('^IXIC', period='6mo')
    btc_df = yf.download('BTC-USD', period='6mo')

    # Verificar se os três vieram com dados válidos
    if not spx_df.empty and not nasdaq_df.empty and not btc_df.empty:
        # Selecionar a coluna correta
        spx_series = spx_df["Adj Close"] if "Adj Close" in spx_df.columns else spx_df["Close"]
        nasdaq_series = nasdaq_df["Adj Close"] if "Adj Close" in nasdaq_df.columns else nasdaq_df["Close"]
        btc_series = btc_df["Adj Close"] if "Adj Close" in btc_df.columns else btc_df["Close"]

        # Renomear as séries e montar o DataFrame
        comparativo = pd.concat([
            spx_series.rename("S&P 500"),
            nasdaq_series.rename("Nasdaq"),
            btc_series.rename("Bitcoin")
        ], axis=1).dropna()

        # Normalizar
        comparativo = comparativo / comparativo.iloc[0]

        # Mostrar gráfico
        st.line_chart(comparativo)
    else:
        st.warning("⚠️ Não foi possível carregar dados de um ou mais ativos (SP500, Nasdaq ou BTC). Tente novamente mais tarde.")

except Exception as e:
    st.error("❌ Erro ao processar o comparativo. Detalhes no log do Streamlit.")



# --- ALERTA AUTOMÁTICO (placeholder) ---
if last_delta_bilhoes < -50:
    st.error("🚨 Alerta: Liquidez caiu mais de $50B. Enviar alerta via n8n/WhatsApp!")

# --- GRÁFICO DE REPO/RRP (em breve) ---
st.subheader("💵 Repos e Reverse Repos (em breve)")
st.caption("Integração em desenvolvimento com dados do New York Fed")
