import pandas as pd
import yfinance as yf
import requests
import matplotlib.pyplot as plt
import seaborn as sns

# Import Greed and Fear data
url = "https://api.alternative.me/fng/?limit=0"

response = requests.get(url)
data = response.json()

df_fng = pd.DataFrame(data["data"])

df_fng["date"] = pd.to_datetime(df_fng["timestamp"], unit="s")
df_fng = df_fng.set_index("date")
df_fng = df_fng.sort_index()

df_fng["fng_value"] = df_fng["value"].astype(int)
df_fng = df_fng[["fng_value"]]

start_date = df_fng.index[0]

# Import BTC data
df_btc = yf.download("BTC-USD", start = start_date)

df_btc = df_btc[["Close"]].copy()
df_btc.columns = ['btc_price']

# Union of the two dfs
df = pd.merge(df_fng, df_btc, left_index=True, right_index=True, how="inner")

print(f"Starting date: {df.index[0]}")
# Spearman correlation
correlation = df["fng_value"].corr(df["btc_price"], method="spearman")
print(f"Spearman correlation: {correlation}")

# Threashold analysis
bins = [0, 25, 45, 55, 75, 100]
labels = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']

df["Category"] = pd.cut(df["fng_value"], bins=bins, labels=labels)

df['Return_7d'] = df['btc_price'].pct_change(7).shift(-7) * 100
df['Return_30d'] = df['btc_price'].pct_change(30).shift(-30) * 100
df['Return_90d'] = df['btc_price'].pct_change(90).shift(-90) * 100
df['Return_180d'] = df['btc_price'].pct_change(180).shift(-180) * 100
df['Return_365d'] = df['btc_price'].pct_change(365).shift(-365) * 100

def win_rate(x):
    return (x > 0).mean() * 100

cols = ["Return_7d", "Return_30d", "Return_90d", "Return_180d", "Return_365d"]

analysis = df.groupby('Category', observed=False)[cols].agg(["mean", "median", win_rate])

analysis.round(2).to_excel(r"C:\Users\nicco\Documents\VS Code Program\Personal Finance\Sentiment Analysis BTC\Sentiment_Analysis_BTC.xlsx")



# Distributions "Neutral"
neutral_7d = df.loc[df["Category"] == "Neutral", 'Return_7d']
neutral_30d = df.loc[df["Category"] == "Neutral", 'Return_30d']
neutral_90d = df.loc[df["Category"] == "Neutral", 'Return_90d']
neutral_180d = df.loc[df["Category"] == "Neutral", 'Return_180d'] 
neutral_365d = df.loc[df["Category"] == "Neutral", 'Return_365d']

plt.figure()
sns.histplot(neutral_7d, kde = True)
plt.show()

# Average time spent in Neutral zone
df["Block_ID"] = (df["Category"] != df["Category"].shift(1)).cumsum()
neutral_days = df[df["Category"] == "Neutral"]
neutral_streaks = neutral_days.groupby('Block_ID').size()
average_neutral_days = neutral_streaks.mean()
print(f"If we enter the Neutral zone, we stay there on average for: {average_neutral_days:.2f} days")

plt.figure()
sns.histplot(neutral_streaks)
plt.show()


# In greed and extreme greed, on average, after how many days do we get the first loss?
def count_days(row):
    current_date = row.name
    current_price = row["btc_price"]
    category = row["Category"]

    future_data = df.loc[current_date:].iloc[1:]

    if category in ['Extreme Fear', 'Fear']:
        target_dates = future_data[future_data["btc_price"] > current_price]

    if category in ['Neutral', 'Greed', 'Extreme Greed']:
        target_dates = future_data[future_data['btc_price'] < current_price]

    if not target_dates.empty:
        first_date = target_dates.index[0]
        return (first_date - current_date).days
    else:
        return None
    
df['Days_Until_Flip'] = df.apply(count_days, axis=1)

# Group by Category to see the average days
result = df.groupby('Category', observed=False)['Days_Until_Flip'].mean()

print(result)