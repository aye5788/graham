import requests
import streamlit as st

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
            st.write("DCF API Response Debug:", data)  # Debugging
            
            # Handle list response
            if isinstance(data, list) and len(data) > 0:
                dcf_value = data[0].get("dcf", "N/A")  # Extract from the first element
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
