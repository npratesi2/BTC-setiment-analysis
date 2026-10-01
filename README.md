# Bitcoin Sentiment & Return Analysis

An analytical project investigating the relationship between the **Crypto Fear & Greed Index** and subsequent **Bitcoin (BTC) forward returns** across multiple time horizons (7, 30, 90, 180, and 365 days).

---

## 📌 Overview

The project queries daily sentiment values directly from the [Alternative.me Fear and Greed API](https://alternative.me/crypto/fear-and-greed-index/) and pairs them with historical daily price action retrieved via `yfinance`. 

Key questions addressed:
- Does extreme sentiment provide an edge for forward returns?
- What are the win rates and median performances when buying under different sentiment regimes?
- How long does Bitcoin typically linger in the "Neutral" sentiment zone?
- How many days does it take, on average, to observe the first price drop or rebound after entering a given sentiment state?
