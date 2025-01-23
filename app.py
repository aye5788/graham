import requests
import streamlit as st
import time

# Fetch Financial Data from Alpha Vantage - Overview
def fetch_financial_data(ticker):
    api_key = "RUSJILJHKEEHEMJ7"  # Alpha Vantage API Key
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Ensure the response contains valid data
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
        # Debugging the response structure
        st.write("Alpha Vantage CASH_FLOW Response Debug:", data)
        try:
            annual_data = data.get("annualReports", [])
            if annual_data:
                # Use the most recent year's free cash flow value
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
        # Debugging the response structure
        st.write("FMP Key Metrics Response Debug:", data)
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

# Generate Insights with Cohere
def generate_cohere_insights(metrics):
    cohere_api_key = "i6rCnd8kHKs3DKmfo2glf48xftmfyOZ9kmuP9Gqc"  # Cohere API Key
    cohere_endpoint = "https://api.cohere.ai/generate"
    payload = {
        "model": "command-xlarge-nightly",  # Replace with available model if necessary
        "prompt": f"Provide insights on the following financial metrics: {metrics}",
        "max_tokens": 300,
        "temperature": 0.7
    }
    headers = {"Authorization": f"Bearer {cohere_api_key}"}
    response = requests.post(cohere_endpoint, json=payload, headers=headers)

    if response.status_code == 200:
        try:
            response_json = response.json()
            if "generations" in response_json:
                return response_json["generations"][0]["text"]
            else:
                raise ValueError("Unexpected response structure")
        except Exception as e:
            st.error(f"Failed to parse Cohere response: {e}")
            st.write("Cohere Response Debug:", response.text)
            return None
    else:
        st.error(f"Failed to generate insights with Cohere. Status code: {response.status_code}")
        st.write("Cohere API Debug:", response.text)
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

            # Generate Cohere AI Insights
            metrics = {
                "Revenue Growth": f"{revenue_growth:.1f}%" if revenue_growth else "N/A",
                "Net Income Growth": f"{net_income_growth:.1f}%" if net_income_growth else "N/A",
                "EPS Growth": f"{eps_growth:.1f}%" if eps_growth else "N/A",
                "Operating Cash Flow Growth": f"{operating_cf_growth:.1f}%" if operating_cf_growth else "N/A",
                "Free Cash Flow Growth": f"{fcf_growth:.1f}%" if fcf_growth else "N/A"
            }
            insights = generate_cohere_insights(metrics)
            if insights:
                st.subheader("Cohere AI Insights")
                st.write(insights)
            else:
                st.error("Failed to generate insights with Cohere.")

