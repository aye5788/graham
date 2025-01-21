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
    api_key = "CLP9IN76G4S8OUXN"
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
    api_key = "CLP9IN76G4S8OUXN"
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

# Calculate Price-to-Sales (P/S) Ratio and Suggested Price
def calculate_ps_ratio(data):
    try:
        market_cap = float(data.get("MarketCapitalization", 0))
        revenue = float(data.get("RevenueTTM", 0))  # Total Revenue (Trailing Twelve Months)
        shares_outstanding = float(data.get("SharesOutstanding", 0))  # Shares Outstanding

        if revenue > 0 and shares_outstanding > 0:
            ps_ratio = market_cap / revenue
            suggested_price = (ps_ratio * revenue) / shares_outstanding  # Suggested fair price based on P/S ratio
            return round(ps_ratio, 2), round(suggested_price, 2)
        else:
            return None, None
    except Exception:
        return None, None

# Discounted Cash Flow (DCF) Model
def calculate_dcf(data, growth_rate=0.1, discount_rate=0.08, years=5):
    try:
        # Fetch Free Cash Flow from the CASH_FLOW endpoint
        fcf = fetch_free_cash_flow(data['Symbol'])
        shares_outstanding = float(data.get("SharesOutstanding", 0))  # Shares Outstanding

        # Check if we successfully retrieved Free Cash Flow
        if fcf is None or fcf <= 0:
            st.write("Free Cash Flow data is missing or invalid. Using a baseline value for calculation.")
            fcf = 100000000  # Baseline free cash flow value (for non-profitable companies)

        dcf_value = 0
        for t in range(1, years + 1):
            projected_fcf = fcf * (1 + growth_rate) ** t
            dcf_value += projected_fcf / (1 + discount_rate) ** t

        # Suggested price based on DCF
        if shares_outstanding > 0:
            suggested_price = dcf_value / shares_outstanding
            return round(dcf_value, 2), round(suggested_price, 2)
        else:
            return None, None
    except Exception:
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
            price_change_1y = calculate_ps_ratio(data)
            st.subheader(f"Growth Stock Analysis for {ticker}")
            st.write(f"**Quarterly Revenue Growth (YOY):** {revenue_growth}")
            st.write(f"**Market Capitalization:** {market_cap}")
            st.write(f"**1-Year Price Change:** {price_change_1y}")

        elif menu == "Stock Valuation (P/S Ratio)":
            # Calculate P/S Ratio and suggested price
            ps_ratio, suggested_price = calculate_ps_ratio(data)
            if ps_ratio:
                st.subheader(f"P/S Ratio Valuation for {ticker}")
                st.write(f"**Price-to-Sales (P/S) Ratio:** {ps_ratio}")
                st.write(f"**Suggested Fair Price:** ${suggested_price}")

                # Compare with real-time price
                if real_time_price:
                    st.write(f"**Current Price:** ${real_time_price}")
                    if real_time_price < suggested_price:
                        st.write("**Interpretation:** The stock is currently underpriced.")
                    elif real_time_price > suggested_price:
                        st.write("**Interpretation:** The stock is currently overpriced.")
                    else:
                        st.write("**Interpretation:** The stock is fairly priced based on the P/S ratio.")

            else:
                st.write("P/S Ratio could not be calculated. Please ensure MarketCap and Revenue data are available.")

        elif menu == "DCF Model Valuation":
            # Calculate DCF (Discounted Cash Flow) Value and suggested price
            dcf_value, suggested_price = calculate_dcf(data)
            if dcf_value:
                st.subheader(f"DCF Model Valuation for {ticker}")
                st.write(f"**Discounted Cash Flow (DCF) Valuation:** ${dcf_value}")
                st.write(f"**Suggested Fair Price:** ${suggested_price}")

                # Compare with real-time price
                if real_time_price:
                    st.write(f"**Current Price:** ${real_time_price}")
                    if real_time_price < suggested_price:
                        st.write("**Interpretation:** The stock is currently underpriced.")
                    elif real_time_price > suggested_price:
                        st.write("**Interpretation:** The stock is currently overpriced.")
                    else:
                        st.write("**Interpretation:** The stock is fairly priced based on DCF.")

            else:
                st.write("DCF Valuation could not be calculated. Please ensure Free Cash Flow data are available.")

