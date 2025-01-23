import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Fetch Financial Data from Alpha Vantage - Overview
def fetch_financial_data(ticker):
    api_key = "RUSJILJHKEEHEMJ7"  # Alpha Vantage API Key
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "Symbol" in data:
            return data
        else:
            st.error("No data found in Alpha Vantage Overview response.")
            return None
    else:
        st.error(f"Alpha Vantage Overview request failed. Status code: {response.status_code}")
        return None

# Fetch DCF Valuation from FMP DCF Reports API
def fetch_dcf_valuation(ticker):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"  # FMP API Key
    url = f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{ticker}?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                dcf_value = data[0].get("dcf", "N/A")
                stock_price = data[0].get("Stock Price", "N/A")
                date = data[0].get("date", "N/A")
                return {"DCF Value": dcf_value, "Stock Price": stock_price, "Valuation Date": date}
            else:
                st.error("Unexpected response structure. DCF data not available.")
                return None
        except Exception as e:
            st.error(f"Error parsing DCF data: {e}")
            return None
    else:
        st.error(f"Failed to fetch DCF valuation. Status code: {response.status_code}")
        return None

# Fetch Financial Growth Data
def fetch_financial_growth_data(ticker):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"  # FMP API Key
    url = f"https://financialmodelingprep.com/api/v3/financial-growth/{ticker}?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error(f"Failed to fetch financial growth data. Status code: {response.status_code}")
        return None

# Plot Growth Metrics
def plot_growth_metrics(growth_data):
    if growth_data:
        # Convert to DataFrame
        df = pd.DataFrame(growth_data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Select metrics for visualization
        metrics = {
            "Cashflow Growth": "freeCashFlowGrowth",
            "Income Growth": "netIncomeGrowth",
            "Balance Sheet Growth": "totalAssetsGrowth",
            "Financial Growth": "totalEquityGrowth"
        }

        # Plot each metric
        for title, metric in metrics.items():
            if metric in df.columns:
                plt.figure(figsize=(10, 6))
                plt.plot(df.index, df[metric].astype(float) * 100, marker='o')
                plt.title(f"{title} Over Time", fontsize=16)
                plt.ylabel("Growth (%)", fontsize=12)
                plt.xlabel("Date", fontsize=12)
                plt.grid(True)
                st.pyplot(plt)
            else:
                st.warning(f"{metric} data not available.")

# Streamlit App
st.title("Enhanced Stock Analysis Tool")

# Sidebar Menu
menu = st.sidebar.radio("Select Analysis Type", ["Stock Valuation (P/S Ratio)", "Growth Stock Analysis", "DCF Model Valuation"])

# User Input
ticker = st.text_input("Enter Stock Ticker:", value="AAPL").upper()

if st.button("Run Analysis"):
    # Fetch data from Alpha Vantage Overview
    data = fetch_financial_data(ticker)
    if data:
        # Display DCF Model Valuation
        if menu == "DCF Model Valuation":
            dcf_data = fetch_dcf_valuation(ticker)
            if dcf_data:
                st.subheader(f"DCF Model Valuation for {ticker}")
                st.write("### Valuation Summary")
                st.write(f"**Discounted Cash Flow (DCF) Value:** ${dcf_data['DCF Value']}")
                st.write(f"**Stock Price:** ${dcf_data['Stock Price']}")
                st.write(f"**Valuation Date:** {dcf_data['Valuation Date']}")

        # Display Growth Stock Analysis
        if menu == "Growth Stock Analysis":
            growth_data = fetch_financial_growth_data(ticker)
            if growth_data:
                st.subheader(f"Growth Stock Analysis for {ticker}")
                st.write("### Visualized Growth Metrics")
                plot_growth_metrics(growth_data)
