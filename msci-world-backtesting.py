import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# =========================
# 1. Descargar datos
# =========================

ticker = "0P0001CLDK.F"  # Fidelity MSCI World Index Fund

data = yf.download(ticker, start="2018-01-01", end="2026-01-01")

data = data[["Close"]].dropna()

# =========================
# 2. Medias móviles
# =========================

data["MA50"] = data["Close"].rolling(window=50).mean()
data["MA200"] = data["Close"].rolling(window=200).mean()

# =========================
# 3. Señal de inversión
# =========================

data["signal"] = 0
data.loc[data["MA50"] > data["MA200"], "signal"] = 1

# =========================
# 4. Rentabilidades
# =========================

data["returns"] = data["Close"].pct_change()

# shift(1) evita usar información del mismo día
data["strategy_returns"] = data["signal"].shift(1) * data["returns"]

data = data.dropna()

# =========================
# 5. Evolución acumulada
# =========================

data["buy_hold"] = (1 + data["returns"]).cumprod()
data["strategy"] = (1 + data["strategy_returns"]).cumprod()

# =========================
# 6. Drawdown
# =========================

data["max_buy_hold"] = data["buy_hold"].cummax()
data["drawdown_buy_hold"] = (data["buy_hold"] - data["max_buy_hold"]) / data["max_buy_hold"]

data["max_strategy"] = data["strategy"].cummax()
data["drawdown_strategy"] = (data["strategy"] - data["max_strategy"]) / data["max_strategy"]

# =========================
# 7. Métricas
# =========================

trading_days = 252

rentabilidad_buy_hold = data["buy_hold"].iloc[-1] - 1
rentabilidad_estrategia = data["strategy"].iloc[-1] - 1

vol_buy_hold = data["returns"].std() * np.sqrt(trading_days)
vol_strategy = data["strategy_returns"].std() * np.sqrt(trading_days)

sharpe_buy_hold = (data["returns"].mean() * trading_days) / vol_buy_hold
sharpe_strategy = (data["strategy_returns"].mean() * trading_days) / vol_strategy

max_drawdown_buy_hold = data["drawdown_buy_hold"].min()
max_drawdown_strategy = data["drawdown_strategy"].min()

dias_invertidos = data["signal"].sum()
dias_fuera = len(data) - dias_invertidos

# =========================
# 8. Resultados
# =========================

print("RESULTADOS BACKTESTING FIDELITY MSCI WORLD")
print("------------------------------------------")

print("Rentabilidad Buy & Hold:", round(rentabilidad_buy_hold * 100, 2), "%")
print("Rentabilidad Estrategia MA50/MA200:", round(rentabilidad_estrategia * 100, 2), "%")

print("Volatilidad Buy & Hold:", round(vol_buy_hold * 100, 2), "%")
print("Volatilidad Estrategia:", round(vol_strategy * 100, 2), "%")

print("Sharpe Buy & Hold:", round(sharpe_buy_hold, 2))
print("Sharpe Estrategia:", round(sharpe_strategy, 2))

print("Máx Drawdown Buy & Hold:", round(max_drawdown_buy_hold * 100, 2), "%")
print("Máx Drawdown Estrategia:", round(max_drawdown_strategy * 100, 2), "%")

print("Días invirtiendo:", int(dias_invertidos))
print("Días fuera del mercado:", int(dias_fuera))

print("\nÚltimos datos:")
print(data[["Close", "MA50", "MA200", "signal"]].tail(20))

# =========================
# 9. Gráfico evolución
# =========================

plt.figure(figsize=(10, 6))
plt.plot(data["buy_hold"], label="Buy & Hold Fidelity MSCI World")
plt.plot(data["strategy"], label="Estrategia MA50/MA200")
plt.title("Backtesting Fidelity MSCI World: Buy & Hold vs Cruce de Medias")
plt.xlabel("Fecha")
plt.ylabel("Crecimiento acumulado")
plt.legend()
plt.grid(True)
plt.show()

# =========================
# 10. Gráfico drawdown
# =========================

plt.figure(figsize=(10, 6))
plt.plot(data["drawdown_buy_hold"], label="Drawdown Buy & Hold")
plt.plot(data["drawdown_strategy"], label="Drawdown Estrategia MA50/MA200")
plt.title("Drawdown: Buy & Hold vs Estrategia MA50/MA200")
plt.xlabel("Fecha")
plt.ylabel("Caída desde máximos")
plt.legend()
plt.grid(True)
plt.show()
