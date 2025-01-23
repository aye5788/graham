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
            st.write("Alpha Vantage Overview Debug:", data)
            return None
    else:
        st.error(f"Alpha Vantage Overview request failed. Status code: {response.status_code}")
        return None

# Fetch Free Cash Flow (FCF) from Alpha Vantage
def fetch_free_cash_flow(ticker):
    api_key = "RUSJILJHKEEHEMJ7"  # Alpha Vantage API Key
    url = f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            annual_data = data.get("annualReports", [])
            if annual_data:
                fcf = float(annual_data[0].get("freeCashFlow", 0))
                return fcf
            else:
                return None
        except (KeyError, ValueError) as e:
            st.error(f"Error parsing Free Cash Flow data: {e}")
            return None
    else:
        st.error(f"Failed to fetch Free Cash Flow data. Status code: {response.status_code}")
        return None

# Fetch EPS Data from Financial Modeling Prep
def fetch_eps_data(ticker):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"  # FMP API Key
    url = f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?period=annual&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            if data:
                eps_growth = data[0].get("epsGrowth", 0)
                return eps_growth
            else:
                return 0
        except (KeyError, IndexError) as e:
            st.error(f"Error parsing EPS data: {e}")
            return 0
    else:
        st.error(f"Failed to fetch EPS data. Status code: {response.status_code}")
        return 0

# Fetch DCF Valuation from FMP DCF Reports API
def fetch_dcf_valuation(ticker):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"  # FMP API Key
    url = f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{ticker}?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        st.write("DCF API Response Debug:", data)  # Debugging
        try:
            dcf_value = data.get("dcf", "N/A")  # Default to N/A if not found
            date = data.get("date", "N/A")
            return dcf_value, date
        except KeyError:
            st.error("DCF data not found in the response.")
            return "N/A", "N/A"
    else:
        st.error(f"Failed to fetch DCF valuation. Status code: {response.status_code}")
        return "N/A", "N/A"

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
        # Fetch EPS Growth from FMP
        eps_growth = fetch_eps_data(ticker)
        # Fetch Free Cash Flow Growth from Alpha Vantage
        fcf_growth = fetch_free_cash_flow(ticker)

        # Display Growth Stock Analysis
        if menu == "Growth Stock Analysis":
            revenue_growth = float(data.get("RevenueGrowth", 0)) * 100
            net_income_growth = float(data.get("NetIncomeGrowth", 0)) * 100
            operating_cf_growth = float(data.get("OperatingCashFlowGrowth", 0)) * 100

            st.subheader(f"Growth Stock Analysis for {ticker}")
            st.write(f"**Revenue Growth (YoY):** {revenue_growth:.1f}%" if revenue_growth else "**Revenue Growth (YoY):** N/A")
            st.write(f"**Net Income Growth (YoY):** {net_income_growth:.1f}%" if net_income_growth else "**Net Income Growth (YoY):** N/A")
            st.write(f"**EPS Growth (YoY):** {eps_growth:.1f}%" if eps_growth else "**EPS Growth (YoY):** N/A")
            st.write(f"**Operating Cash Flow Growth (YoY):** {operating_cf_growth:.1f}%" if operating_cf_growth else "**Operating Cash Flow Growth (YoY):** N/A")
            st.write(f"**Free Cash Flow Growth (YoY):** {fcf_growth:.1f}%" if fcf_growth else "**Free Cash Flow Growth (YoY):** N/A")

        # Display DCF Model Valuation
        if menu == "DCF Model Valuation":
            dcf_valuation, valuation_date = fetch_dcf_valuation(ticker)
            st.subheader(f"DCF Valuation for {ticker}")
            st.write(f"**Discounted Cash Flow (DCF) Value:** ${dcf_valuation}" if dcf_valuation != "N/A" else "**DCF Value:** Data not available.")
            st.write(f"**Valuation Date:** {valuation_date}" if valuation_date != "N/A" else "**Valuation Date:** Data not available.")
