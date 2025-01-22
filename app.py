import requests
import streamlit as st
from cohere import Client

# Initialize Cohere API
COHERE_API_KEY = "i6rCnd8kHKs3DKmfo2glf48xftmfyOZ9kmuP9Gqc"
cohere_client = Client(COHERE_API_KEY)

# Fetch data from FMP API
def fetch_fmp_data(endpoint, ticker, period="annual", limit=1):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{ticker}?period={period}&limit={limit}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            return data if isinstance(data, list) else [data]
        except ValueError:
            st.error("Invalid response received from API.")
            return []
    else:
        st.error(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return []

# Format and display growth metrics
def display_growth_metrics(title, metrics):
    st.subheader(title)
    if metrics:
        for key, value in metrics.items():
            # Convert to percentage and round to two decimals
            if isinstance(value, (int, float)):
                st.write(f"**{key.replace('growth', '').capitalize()}**: {round(value * 100, 2)}%")
    else:
        st.write("No relevant data available.")

# Generate insights using Cohere AI
def generate_cohere_insights(metrics):
    try:
        prompt = f"""Analyze the following growth metrics and provide key insights and action points for investors:
        {metrics}
        """
        response = cohere_client.generate(
            model="command-xlarge-nightly",
            prompt=prompt,
            max_tokens=300,
        )
        return response.generations[0].text.strip()
    except Exception as e:
        st.error(f"Failed to generate insights with Cohere: {e}")
        return None

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

# Streamlit App
st.title("Enhanced Stock Analysis Tool")

# Sidebar Menu
menu = st.sidebar.radio("Select Analysis Type", ["Stock Valuation (P/S Ratio)", "Growth Stock Analysis", "DCF Model Valuation", "Financial Metrics Analysis"])

# User Input
ticker = st.text_input("Enter Stock Ticker:", value="AAPL").upper()

if st.button("Run Analysis"):
    if menu == "Growth Stock Analysis":
        st.subheader(f"Growth Stock Analysis for {ticker}")
        data = fetch_financial_data(ticker)
        if data:
            revenue_growth = float(data.get("QuarterlyRevenueGrowthYOY", 0))
            net_income_growth = float(data.get("NetIncomeGrowth", 0))
            st.write(f"**Revenue Growth (YoY):** {round(revenue_growth * 100, 2)}%")
            st.write(f"**Net Income Growth (YoY):** {round(net_income_growth * 100, 2)}%")

        # Fetch Financial Growth Metrics
        financial_growth_data = fetch_fmp_data("financial-growth", ticker)
        if financial_growth_data:
            display_growth_metrics("Financial Growth Metrics", financial_growth_data[0])

        # Fetch Income Growth Metrics
        income_growth_data = fetch_fmp_data("income-statement-growth", ticker)
        if income_growth_data:
            display_growth_metrics("Income Growth Metrics", income_growth_data[0])

        # Fetch Balance Sheet Growth Metrics
        balance_sheet_growth_data = fetch_fmp_data("balance-sheet-statement-growth", ticker)
        if balance_sheet_growth_data:
            display_growth_metrics("Balance Sheet Growth Metrics", balance_sheet_growth_data[0])

        # Generate insights with Cohere AI
        st.subheader("Cohere AI Insights")
        metrics = {
            "revenue_growth": revenue_growth,
            "net_income_growth": net_income_growth,
            **financial_growth_data[0] if financial_growth_data else {},
            **income_growth_data[0] if income_growth_data else {},
            **balance_sheet_growth_data[0] if balance_sheet_growth_data else {},
        }
        insights = generate_cohere_insights(metrics)
        if insights:
            st.write(insights)

    elif menu == "Stock Valuation (P/S Ratio)":
        data = fetch_financial_data(ticker)
        if data:
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
        real_time_price = fetch_real_time_price(ticker)
        dcf_value = fetch_dcf_valuation(ticker)

        if dcf_value:
            st.subheader(f"DCF Model Valuation for {ticker}")
            st.write(f"**DCF Valuation:** ${round(dcf_value, 2)}")
            if real_time_price:
                st.write(f"**Current Price:** ${round(real_time_price, 2)}")

    elif menu == "Financial Metrics Analysis":
        # Fetch and display key metrics
        key_metrics_data = fetch_fmp_data("key-metrics", ticker)
        if key_metrics_data:
            st.subheader("Key Metrics")
            for metric, value in key_metrics_data[0].items():
                if isinstance(value, (int, float)):
                    st.write(f"**{metric.replace('_', ' ').capitalize()}**: {value}")

