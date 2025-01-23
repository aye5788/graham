import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Fetch growth data from the appropriate API
def fetch_growth_data(endpoint, ticker):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"  # FMP API Key
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{ticker}?period=annual&limit=10&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return None

# Combine and process growth data from multiple APIs
def process_growth_data(ticker):
    # Fetch data from different growth endpoints
    cashflow_growth = fetch_growth_data("cash-flow-statement-growth", ticker)
    income_growth = fetch_growth_data("income-statement-growth", ticker)
    balance_sheet_growth = fetch_growth_data("balance-sheet-statement-growth", ticker)

    # Combine data into a single DataFrame
    combined_data = []
    if cashflow_growth:
        for record in cashflow_growth:
            record['type'] = 'Cashflow Growth'
            combined_data.append(record)
    if income_growth:
        for record in income_growth:
            record['type'] = 'Income Growth'
            combined_data.append(record)
    if balance_sheet_growth:
        for record in balance_sheet_growth:
            record['type'] = 'Balance Sheet Growth'
            combined_data.append(record)

    return pd.DataFrame(combined_data)

# Plot bar charts for growth metrics
def plot_growth_bars(df):
    if not df.empty:
        for growth_type in df['type'].unique():
            data = df[df['type'] == growth_type]
            plt.figure(figsize=(12, 6))
            plt.bar(
                data['date'],
                data['growthNetIncome'].astype(float) * 100,
                color='teal',
                edgecolor='black',
                width=0.6,
            )
            plt.title(f"{growth_type} Over Time", fontsize=16, fontweight='bold')
            plt.ylabel("Growth (%)", fontsize=12)
            plt.xlabel("Year", fontsize=12)
            plt.xticks(rotation=45, fontsize=10)
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            st.pyplot(plt)
    else:
        st.warning("No growth data available for visualization.")

# Streamlit App
st.title("Enhanced DCF and Growth Analysis")

# User Input
ticker = st.text_input("Enter Stock Ticker:", value="AAPL").upper()

if st.button("Run Analysis"):
    st.subheader(f"Growth Metrics for {ticker}")
    growth_data = process_growth_data(ticker)
    if not growth_data.empty:
        plot_growth_bars(growth_data)
    else:
        st.error("No growth data available for the selected ticker.")
