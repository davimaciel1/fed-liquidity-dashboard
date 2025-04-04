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
# --- COMPARATIVO COM ATIVOS USANDO FINNHUB ---
import time

st.subheader("📈 Comparativo com SP500, Nasdaq e BTC")

FINNHUB_API_KEY = "cvo1311r01qppf5a7ihgcvo1311r01qppf5a7ii0"

def get_finnhub_series(symbol, is_crypto=False):
    end = int(time.time())
    start = end - 60 * 60 * 24 * 180  # Últimos 6 meses
    market = "BINANCE:BTCUSDT" if is_crypto else symbol
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={market}&resolution=D&from={start}&to={end}&token={FINNHUB_API_KEY}"
    res = requests.get(url).json()

    if res.get("s") != "ok":
        return pd.Series(dtype="float64")

    df = pd.DataFrame({
        "timestamp": res["t"],
        "close": res["c"]
    })
    df["Data"] = pd.to_datetime(df["timestamp"], unit="s")
    return df.set_index("Data")["close"]

try:
    spx = get_finnhub_series("SPY")  # ETF do S&P 500
    ndx = get_finnhub_series("QQQ")  # ETF do Nasdaq
    btc = get_finnhub_series("BINANCE:BTCUSDT", is_crypto=True)

    if spx.empty or ndx.empty or btc.empty:
        st.warning("⚠️ Não foi possível obter dados de SP500, Nasdaq ou BTC.")
    else:
        comparativo = pd.concat([
            spx.rename("S&P 500"),
            ndx.rename("Nasdaq"),
            btc.rename("Bitcoin")
        ], axis=1).dropna()

        comparativo = comparativo / comparativo.iloc[0]
        st.line_chart(comparativo)

except Exception as e:
    st.error(f"❌ Erro ao buscar dados da Finnhub: {e}")




# --- ALERTA AUTOMÁTICO (placeholder) ---
if last_delta_bilhoes < -50:
    st.error("🚨 Alerta: Liquidez caiu mais de $50B. Enviar alerta via n8n/WhatsApp!")

# --- GRÁFICO DE REPO/RRP (em breve) ---
st.subheader("💵 Repos e Reverse Repos (em breve)")
st.caption("Integração em desenvolvimento com dados do New York Fed")
