import requests
import streamlit as st
import cohere

# Initialize Cohere API
COHERE_API_KEY = "i6rCnd8kHKs3DKmfo2glf48xftmfyOZ9kmuP9Gqc"
co = cohere.Client(COHERE_API_KEY)

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

# Fetch Data from FMP
def fetch_fmp_data(ticker, endpoint):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{ticker}?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data from {endpoint}. Status code: {response.status_code}")
        return None

# Fetch Real-Time Price from Alpha Vantage
def fetch_real_time_price(ticker):
    api_key = "RUSJILJHKEEHEMJ7"
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=1min&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            last_refreshed = data["Meta Data"]["3. Last Refreshed"]
            real_time_price = float(data["Time Series (1min)"][last_refreshed]["4. close"])
            return real_time_price
        except KeyError:
            return None
    else:
        st.error(f"Failed to fetch real-time price. Status code: {response.status_code}")
        return None

# Cohere AI Interpretation
def interpret_outputs(output_type, data):
    prompt = f"Given the following {output_type} data: {data}, provide a summary and actionable insights for an investor."
    try:
        response = co.generate(
            model="xlarge",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
        )
        return response.generations[0].text.strip()
    except Exception as e:
        st.error("Failed to generate insights with Cohere.")
        return None

# Helper function to format metrics
def format_metric(value):
    if value is not None:
        return f"{value * 100:.2f}%"  # Convert to percentage and round to 2 decimal places
    return "N/A"

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

        if menu == "Growth Stock Analysis":
            # Fetch Growth Metrics
            income_growth_data = fetch_fmp_data(ticker, "income-statement-growth")
            cashflow_growth_data = fetch_fmp_data(ticker, "cash-flow-statement-growth")

            st.subheader(f"Growth Stock Analysis for {ticker}")

            growth_data = {}
            if income_growth_data and isinstance(income_growth_data, list):
                latest_income_growth = income_growth_data[0]
                growth_data["Revenue Growth (YoY)"] = format_metric(latest_income_growth.get('growthRevenue'))
                growth_data["Net Income Growth (YoY)"] = format_metric(latest_income_growth.get('growthNetIncome'))
                growth_data["EPS Growth (YoY)"] = format_metric(latest_income_growth.get('growthEPS'))
                st.write(f"**Revenue Growth (YoY):** {growth_data['Revenue Growth (YoY)']}")
                st.write(f"**Net Income Growth (YoY):** {growth_data['Net Income Growth (YoY)']}")
                st.write(f"**EPS Growth (YoY):** {growth_data['EPS Growth (YoY)']}")

            if cashflow_growth_data and isinstance(cashflow_growth_data, list):
                latest_cashflow_growth = cashflow_growth_data[0]
                growth_data["Operating Cash Flow Growth (YoY)"] = format_metric(latest_cashflow_growth.get('growthOperatingCashFlow'))
                growth_data["Free Cash Flow Growth (YoY)"] = format_metric(latest_cashflow_growth.get('growthFreeCashFlow'))
                st.write(f"**Operating Cash Flow Growth (YoY):** {growth_data['Operating Cash Flow Growth (YoY)']}")
                st.write(f"**Free Cash Flow Growth (YoY):** {growth_data['Free Cash Flow Growth (YoY)']}")
            
            # Cohere AI Interpretation
            insights = interpret_outputs("Growth Stock Analysis", growth_data)
            if insights:
                st.subheader("Cohere AI Insights")
                st.write(insights)

        elif menu == "Stock Valuation (P/S Ratio)":
            market_cap = float(data.get("MarketCapitalization", 0))
            revenue = float(data.get("RevenueTTM", 0))
            shares_outstanding = float(data.get("SharesOutstanding", 0))

            valuation_data = {}
            if revenue > 0 and shares_outstanding > 0:
                ps_ratio = market_cap / revenue
                suggested_price = (ps_ratio * revenue) / shares_outstanding
                valuation_data["P/S Ratio"] = round(ps_ratio, 2)
                valuation_data["Suggested Fair Price"] = round(suggested_price, 2)
                st.subheader(f"P/S Ratio Valuation for {ticker}")
                st.write(f"**Price-to-Sales (P/S) Ratio:** {valuation_data['P/S Ratio']}")
                st.write(f"**Suggested Fair Price:** ${valuation_data['Suggested Fair Price']}")

                if real_time_price:
                    valuation_data["Current Price"] = round(real_time_price, 2)
                    percentage_diff = ((real_time_price - suggested_price) / suggested_price) * 100
                    if real_time_price < suggested_price:
                        st.write(f"**Interpretation:** The stock is currently underpriced by {abs(round(percentage_diff, 2))}%.")
                    elif real_time_price > suggested_price:
                        st.write(f"**Interpretation:** The stock is currently overpriced by {abs(round(percentage_diff, 2))}%.")
                    else:
                        st.write("**Interpretation:** The stock is fairly priced based on the P/S ratio.")

                # Cohere AI Interpretation
                insights = interpret_outputs("P/S Ratio Analysis", valuation_data)
                if insights:
                    st.subheader("Cohere AI Insights")
                    st.write(insights)

