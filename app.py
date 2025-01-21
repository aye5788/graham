import requests
import streamlit as st

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

# Fetch Free Cash Flow (FCF) from Alpha Vantage
def fetch_free_cash_flow(ticker):
    api_key = "RUSJILJHKEEHEMJ7"
    url = f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            # Extracting the most recent annual free cash flow
            annual_data = data['annualCashFlow']
            if annual_data:
                # Use the most recent year's free cash flow value
                fcf = float(annual_data[0]['freeCashFlow'])
                return fcf
            else:
                return None
        except KeyError:
            return None
    else:
        st.error(f"Failed to fetch Free Cash Flow data. Status code: {response.status_code}")
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
            # Extract the latest DCF value
            if data:
                dcf_value = float(data[0].get('dcf', 0))
                current_price = float(data[0].get('stockPrice', 0))
                return dcf_value, current_price
            else:
                return None, None
        except KeyError:
            return None, None
    else:
        st.error(f"Failed to fetch DCF valuation. Status code: {response.status_code}")
        return None, None

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
        # Fetch real-time price (optional)
        real_time_price = fetch_real_time_price(ticker)

        if menu == "Growth Stock Analysis":
            # Growth Stock Analysis logic remains unchanged
            revenue_growth = data.get("QuarterlyRevenueGrowthYOY")
            market_cap = data.get("MarketCapitalization")
            st.subheader(f"Growth Stock Analysis for {ticker}")
            st.write(f"**Quarterly Revenue Growth (YOY):** {revenue_growth}")
            st.write(f"**Market Capitalization:** {market_cap}")

        elif menu == "Stock Valuation (P/S Ratio)":
            # Calculate P/S Ratio and suggested price
            market_cap = float(data.get("MarketCapitalization", 0))
            revenue = float(data.get("RevenueTTM", 0))
            shares_outstanding = float(data.get("SharesOutstanding", 0))
            if revenue > 0 and shares_outstanding > 0:
                ps_ratio = market_cap / revenue
                suggested_price = (ps_ratio * revenue) / shares_outstanding
                st.subheader(f"P/S Ratio Valuation for {ticker}")
                st.write(f"**Price-to-Sales (P/S) Ratio:** {round(ps_ratio, 2)}")
                st.write(f"**Suggested Fair Price:** ${round(suggested_price, 2)}")

        elif menu == "DCF Model Valuation":
            # Fetch and display DCF valuation using FMP
            dcf_value, current_price = fetch_dcf_valuation(ticker)
            if dcf_value:
                st.subheader(f"DCF Model Valuation for {ticker}")
                st.write(f"**Discounted Cash Flow (DCF) Valuation:** ${round(dcf_value, 2)}")
                st.write(f"**Current Price (FMP):** ${round(current_price, 2)}")
                if current_price < dcf_value:
                    st.write("**Interpretation:** The stock is currently underpriced.")
                elif current_price > dcf_value:
                    st.write("**Interpretation:** The stock is currently overpriced.")
                else:
                    st.write("**Interpretation:** The stock is fairly priced.")
            else:
                st.write("DCF Valuation could not be retrieved. Please ensure the ticker is correct and data is available.")
