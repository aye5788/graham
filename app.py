import requests
import streamlit as st

# Function to fetch financial growth data
def fetch_financial_growth_data(ticker, endpoint):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{ticker}?period=annual&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return None

# Function to fetch real-time price
def fetch_real_time_price(ticker):
    api_key = "RUSJILJHKEEHEMJ7"
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=1min&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            last_refreshed = data["Meta Data"]["3. Last Refreshed"]
            return float(data["Time Series (1min)"][last_refreshed]["4. close"])
        except KeyError:
            return None
    else:
        st.error(f"Failed to fetch real-time price. Status code: {response.status_code}")
        return None

# Function to generate insights with Cohere AI
def generate_cohere_insights(metrics):
    cohere_api_key = "i6rCnd8kHKs3DKmfo2glf48xftmfyOZ9kmuP9Gqc"
    cohere_endpoint = "https://api.cohere.ai/generate"
    payload = {
        "model": "command-xlarge",
        "prompt": f"Provide insights on the following financial metrics: {metrics}",
        "max_tokens": 300,
        "temperature": 0.7
    }
    headers = {"Authorization": f"Bearer {cohere_api_key}"}
    response = requests.post(cohere_endpoint, json=payload, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()["generations"][0]["text"]
        except KeyError:
            st.error("Failed to parse Cohere response. Ensure the model ID and API key are correct.")
            return None
    else:
        st.error(f"Failed to generate insights with Cohere. Status code: {response.status_code}")
        return None

# Streamlit app setup
st.title("Enhanced Stock Analysis Tool")

menu = st.sidebar.radio("Select Analysis Type", ["Growth Stock Analysis", "DCF Model Valuation"])

ticker = st.text_input("Enter Stock Ticker:", value="AAPL").upper()

if st.button("Run Analysis"):
    if menu == "Growth Stock Analysis":
        # Fetch financial growth data
        financial_growth_data = fetch_financial_growth_data(ticker, "financial-growth")
        income_growth_data = fetch_financial_growth_data(ticker, "income-statement-growth")
        balance_sheet_growth_data = fetch_financial_growth_data(ticker, "balance-sheet-statement-growth")

        # Extract metrics
        revenue_growth = (
            financial_growth_data[0].get("revenueGrowth", 0) * 100 if financial_growth_data else 0
        )
        net_income_growth = (
            income_growth_data[0].get("growthNetIncome", 0) * 100 if income_growth_data else 0
        )
        eps_growth = (
            financial_growth_data[0].get("epsgrowth", 0) * 100 if financial_growth_data else 0
        )
        operating_cash_flow_growth = (
            financial_growth_data[0].get("operatingCashFlowGrowth", 0) * 100
            if financial_growth_data
            else 0
        )
        free_cash_flow_growth = (
            financial_growth_data[0].get("freeCashFlowGrowth", 0) * 100
            if financial_growth_data
            else 0
        )

        # Display Growth Stock Analysis
        st.subheader(f"Growth Stock Analysis for {ticker}")
        st.write(f"**Revenue Growth (YoY):** {revenue_growth:.1f}%")
        st.write(f"**Net Income Growth (YoY):** {net_income_growth:.1f}%")
        st.write(f"**EPS Growth (YoY):** {eps_growth:.1f}%")
        st.write(f"**Operating Cash Flow Growth (YoY):** {operating_cash_flow_growth:.1f}%")
        st.write(f"**Free Cash Flow Growth (YoY):** {free_cash_flow_growth:.1f}%")

        # Generate insights using Cohere AI
        st.subheader("Cohere AI Insights")
        metrics = {
            "Revenue Growth": f"{revenue_growth:.1f}%",
            "Net Income Growth": f"{net_income_growth:.1f}%",
            "EPS Growth": f"{eps_growth:.1f}%",
            "Operating Cash Flow Growth": f"{operating_cash_flow_growth:.1f}%",
            "Free Cash Flow Growth": f"{free_cash_flow_growth:.1f}%"
        }
        insights = generate_cohere_insights(metrics)
        if insights:
            st.markdown(
                f"""
                <div style="word-wrap: break-word; white-space: pre-wrap;">
                    {insights}
                </div>
                """,
                unsafe_allow_html=True
            )
    elif menu == "DCF Model Valuation":
        # Placeholder for DCF Model Valuation
        st.write("DCF Model Valuation is under development.")

