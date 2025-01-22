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

# Cohere integration for insights
def interpret_outputs(prompt, data):
    cohere_api_key = "i6rCnd8kHKs3DKmfo2glf48xftmfyOZ9kmuP9Gqc"
    cohere_endpoint = "https://api.cohere.ai/v1/generate"
    headers = {"Authorization": f"Bearer {cohere_api_key}"}
    payload = {
        "model": "command-xlarge-nightly",
        "prompt": f"{prompt}: {data}",
        "max_tokens": 100,
        "temperature": 0.7,
    }
    response = requests.post(cohere_endpoint, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["generations"][0]["text"].strip()
    else:
        st.error(f"Failed to generate insights with Cohere. Error: {response.text}")
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
        # Fetch real-time price
        real_time_price = fetch_real_time_price(ticker)

        if menu == "Growth Stock Analysis":
            try:
                revenue_growth = float(data.get("QuarterlyRevenueGrowthYOY", 0)) * 100
                net_income_growth = float(data.get("NetIncomeGrowthYOY", 0)) * 100
                eps_growth = float(data.get("EpsGrowthYOY", 0)) * 100
                operating_cf_growth = float(data.get("OperatingCashFlowGrowthYOY", 0)) * 100
                free_cf_growth = float(data.get("FreeCashFlowGrowthYOY", 0)) * 100
            except ValueError:
                st.error("Error: Some financial metrics could not be converted to numeric values.")

            st.subheader(f"Growth Stock Analysis for {ticker}")
            st.write(f"**Revenue Growth (YoY):** {round(revenue_growth, 2)}%")
            st.write(f"**Net Income Growth (YoY):** {round(net_income_growth, 2)}%")
            st.write(f"**EPS Growth (YoY):** {round(eps_growth, 2)}%")
            st.write(f"**Operating Cash Flow Growth (YoY):** {round(operating_cf_growth, 2)}%")
            st.write(f"**Free Cash Flow Growth (YoY):** {round(free_cf_growth, 2)}%")

            insights = interpret_outputs("growth stock analysis", {
                "Revenue Growth": f"{round(revenue_growth, 2)}%",
                "Net Income Growth": f"{round(net_income_growth, 2)}%",
                "EPS Growth": f"{round(eps_growth, 2)}%",
                "Operating Cash Flow Growth": f"{round(operating_cf_growth, 2)}%",
                "Free Cash Flow Growth": f"{round(free_cf_growth, 2)}%",
            })
            if insights:
                st.subheader("Cohere AI Insights")
                st.write(insights)

        elif menu == "Stock Valuation (P/S Ratio)":
            try:
                market_cap = float(data.get("MarketCapitalization", 0))
                revenue = float(data.get("RevenueTTM", 0))
                shares_outstanding = float(data.get("SharesOutstanding", 0))
            except ValueError:
                st.error("Error: Some financial metrics could not be converted to numeric values.")

            if revenue > 0 and shares_outstanding > 0:
                ps_ratio = market_cap / revenue
                suggested_price = (ps_ratio * revenue) / shares_outstanding
                st.subheader(f"P/S Ratio Valuation for {ticker}")
                st.write(f"**Price-to-Sales (P/S) Ratio:** {round(ps_ratio, 2)}")
                st.write(f"**Suggested Fair Price:** ${round(suggested_price, 2)}")

                if real_time_price:
                    st.write(f"**Current Price (AV):** ${round(real_time_price, 2)}")
                    percentage_diff = ((real_time_price - suggested_price) / suggested_price) * 100
                    if real_time_price < suggested_price:
                        st.write(f"**Interpretation:** The stock is currently underpriced by {abs(round(percentage_diff, 2))}%.")
                    elif real_time_price > suggested_price:
                        st.write(f"**Interpretation:** The stock is currently overpriced by {abs(round(percentage_diff, 2))}%.")
                    else:
                        st.write("**Interpretation:** The stock is fairly priced based on the P/S ratio.")
            else:
                st.write("P/S Ratio could not be calculated. Please ensure MarketCap and Revenue data are available.")

        elif menu == "DCF Model Valuation":
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
                else:
                    st.write("Current price could not be retrieved. Please ensure the ticker is correct and data is available.")
            else:
                st.write("DCF Valuation could not be retrieved. Please ensure the ticker is correct and data is available.")

