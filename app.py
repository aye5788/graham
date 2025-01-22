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

# Fetch additional growth data from FMP
def fetch_fmp_growth_data(ticker, endpoint):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{ticker}?period=annual&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and data:
            return data[0]
    return {}

# Generate insights using Cohere AI
def generate_cohere_insights(metrics):
    cohere_api_key = "i6rCnd8kHKs3DKmfo2glf48xftmfyOZ9kmuP9Gqc"
    url = "https://api.cohere.ai/v1/generate"
    headers = {
        "Authorization": f"Bearer {cohere_api_key}",
        "Content-Type": "application/json"
    }
    prompt = f"The following metrics were provided: {metrics}. Generate insights for investors based on this data."
    payload = {
        "model": "command-xlarge-nightly",
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.7
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return result["generations"][0]["text"]
    else:
        st.error(f"Failed to generate insights with Cohere. Error: {response.status_code}, {response.json()}")
        return None

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
        # Fetch additional financial growth data
        financial_growth_data = fetch_fmp_growth_data(ticker, "financial-growth")
        income_growth_data = fetch_fmp_growth_data(ticker, "income-statement-growth")
        balance_sheet_growth_data = fetch_fmp_growth_data(ticker, "balance-sheet-statement-growth")

        if menu == "Growth Stock Analysis":
            # Growth Stock Analysis
            revenue_growth = round(float(data.get("RevenueGrowthTTM", 0)) * 100, 1)
            net_income_growth = round(float(data.get("NetIncomeGrowthTTM", 0)) * 100, 1)
            eps_growth = round(float(financial_growth_data.get("epsgrowth", 0)) * 100, 1)
            operating_cash_flow_growth = round(float(financial_growth_data.get("operatingCashFlowGrowth", 0)) * 100, 1)
            free_cash_flow_growth = round(float(financial_growth_data.get("freeCashFlowGrowth", 0)) * 100, 1)

            st.subheader(f"Growth Stock Analysis for {ticker}")
            st.write(f"**Revenue Growth (YoY):** {revenue_growth}%")
            st.write(f"**Net Income Growth (YoY):** {net_income_growth}%")
            st.write(f"**EPS Growth (YoY):** {eps_growth}%")
            st.write(f"**Operating Cash Flow Growth (YoY):** {operating_cash_flow_growth}%")
            st.write(f"**Free Cash Flow Growth (YoY):** {free_cash_flow_growth}%")

            # Generate insights with Cohere AI
            st.subheader("Cohere AI Insights")
            metrics = {
                "revenue_growth": revenue_growth,
                "net_income_growth": net_income_growth,
                "eps_growth": eps_growth,
                "operating_cash_flow_growth": operating_cash_flow_growth,
                "free_cash_flow_growth": free_cash_flow_growth
            }
            if financial_growth_data:
                metrics.update(financial_growth_data)
            if income_growth_data:
                metrics.update(income_growth_data)
            if balance_sheet_growth_data:
                metrics.update(balance_sheet_growth_data)
            insights = generate_cohere_insights(metrics)
            if insights:
                st.write(insights)

        elif menu == "Stock Valuation (P/S Ratio)":
            # Stock Valuation
            market_cap = float(data.get("MarketCapitalization", 0))
            revenue = float(data.get("RevenueTTM", 0))
            shares_outstanding = float(data.get("SharesOutstanding", 0))
            if revenue > 0 and shares_outstanding > 0:
                ps_ratio = market_cap / revenue
                suggested_price = (ps_ratio * revenue) / shares_outstanding
                st.subheader(f"P/S Ratio Valuation for {ticker}")
                st.write(f"**Price-to-Sales (P/S) Ratio:** {round(ps_ratio, 2)}")
                st.write(f"**Suggested Fair Price:** ${round(suggested_price, 2)}")
            else:
                st.write("P/S Ratio could not be calculated. Please ensure data is available.")

        elif menu == "DCF Model Valuation":
            # DCF Model Valuation
            dcf_value = fetch_fmp_growth_data(ticker, "discounted-cash-flow")
            if dcf_value:
                st.subheader(f"DCF Model Valuation for {ticker}")
                st.write(f"**Discounted Cash Flow (DCF) Valuation:** ${round(float(dcf_value.get('dcf', 0)), 2)}")
            else:
                st.write("DCF Valuation could not be retrieved. Please ensure the ticker is correct.")

