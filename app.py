import requests
import streamlit as st
import pandas as pd

# Fetch Financial Data from Alpha Vantage - Overview
def fetch_financial_data(ticker):
    api_key = "RUSJILJHKEEHEMJ7"
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API request failed with status code: {response.status_code}")
        return None

# Fetch Real-Time Price from Alpha Vantage
def fetch_real_time_price(ticker):
    api_key = "RUSJILJHKEEHEMJ7"
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=1min&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            # Get the most recent closing price from the time series data
            last_refreshed = data["Meta Data"]["3. Last Refreshed"]
            real_time_price = float(data["Time Series (1min)"][last_refreshed]["4. close"])
            return real_time_price
        except KeyError:
            return None
    else:
        st.error(f"Failed to fetch real-time price. Status code: {response.status_code}")
        return None

# Fetch DCF Valuation from FMP
def fetch_dcf_valuation(ticker):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"
    url = f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{ticker}?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            if data:
                dcf_value = float(data[0].get('dcf', 0))
                return dcf_value
            else:
                return None
        except KeyError:
            return None
    else:
        st.error(f"Failed to fetch DCF valuation. Status code: {response.status_code}")
        return None

# Fetch Additional Metrics from FMP
def fetch_fmp_metrics(ticker, endpoint):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{ticker}?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return None

# Visualize Metrics with Streamlit
def visualize_metrics(data, title):
    st.subheader(title)
    df = pd.DataFrame(data, index=[0])
    st.dataframe(df.T)  # Display as a transposed table

    # Example Bar Chart for Selected Metrics
    st.bar_chart(df.T)

# Streamlit App
st.title("Enhanced Stock Analysis Tool")

# Sidebar Menu
menu = st.sidebar.radio("Select Analysis Type", ["Stock Valuation (P/S Ratio)", "Growth Stock Analysis", "DCF Model Valuation"])

# User Input
ticker = st.text_input("Enter Stock Ticker:", value="AAPL").upper()

if st.button("Run Analysis"):
    # Fetch data from overview
    data = fetch_financial_data(ticker)
    if data:
        # Fetch real-time price
        real_time_price = fetch_real_time_price(ticker)

        if menu == "DCF Model Valuation":
            # Fetch DCF valuation from FMP
            dcf_value = fetch_dcf_valuation(ticker)

            if dcf_value:
                if real_time_price:
                    st.subheader(f"DCF Model Valuation for {ticker}")
                    st.write(f"**Discounted Cash Flow (DCF) Valuation:** ${round(dcf_value, 2)}")
                    st.write(f"**Current Price (AV):** ${round(real_time_price, 2)}")
                    percentage_diff = ((real_time_price - dcf_value) / dcf_value) * 100
                    if real_time_price < dcf_value:
                        st.write(f"**Interpretation:** The stock is currently underpriced by {abs(round(percentage_diff, 2))}%.")
                    elif real_time_price > dcf_value:
                        st.write(f"**Interpretation:** The stock is currently overpriced by {abs(round(percentage_diff, 2))}%.")
                    else:
                        st.write("**Interpretation:** The stock is fairly priced.")

                # Fetch additional financial metrics from FMP
                endpoints = [
                    ("key-metrics", "Key Metrics"),
                    ("ratios", "Ratios"),
                    ("cash-flow-statement-growth", "Cashflow Growth"),
                    ("income-statement-growth", "Income Growth"),
                    ("balance-sheet-statement-growth", "Balance Sheet Growth"),
                    ("enterprise-values", "Enterprise Values"),
                ]
                for endpoint, title in endpoints:
                    metrics = fetch_fmp_metrics(ticker, endpoint)
                    # Filter and prepare relevant data
                    if metrics and isinstance(metrics, list):
                        filtered_metrics = {k: v for k, v in metrics[0].items() if k in [
                            "MarketCap", "RevenuePerShare", "NetIncomePerShare", "PE", "PriceToSalesRatio"
                        ]}
                        visualize_metrics(filtered_metrics, title)
                    elif metrics:
                        visualize_metrics(metrics, title)
            else:
                st.write("DCF Valuation could not be retrieved. Please ensure the ticker is correct and data is available.")

