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

# Fetch Growth Metrics from FMP
def fetch_growth_metrics(ticker, endpoint="income-statement-growth"):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"
    url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{ticker}?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch growth metrics. Status code: {response.status_code}")
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
        real_time_price = None  # Add fetch_real_time_price if needed

        if menu == "Growth Stock Analysis":
            # Fetch growth metrics from FMP
            growth_metrics = fetch_growth_metrics(ticker)

            st.subheader(f"Growth Stock Analysis for {ticker}")
            
            if growth_metrics and isinstance(growth_metrics, list) and len(growth_metrics) > 0:
                metrics = growth_metrics[0]  # Use the first entry
                revenue_growth = metrics.get("growthRevenue", None)
                net_income_growth = metrics.get("growthNetIncome", None)
                free_cash_flow_growth = metrics.get("growthFreeCashFlow", None)
                operating_cash_flow_growth = metrics.get("growthOperatingCashFlow", None)
                roe = metrics.get("returnOnEquity", None)

                # Display the growth metrics
                st.write(f"**Revenue Growth (YoY):** {revenue_growth:.2%}" if revenue_growth else "N/A")
                st.write(f"**Net Income Growth (YoY):** {net_income_growth:.2%}" if net_income_growth else "N/A")
                st.write(f"**Free Cash Flow Growth (YoY):** {free_cash_flow_growth:.2%}" if free_cash_flow_growth else "N/A")
                st.write(f"**Operating Cash Flow Growth (YoY):** {operating_cash_flow_growth:.2%}" if operating_cash_flow_growth else "N/A")
                st.write(f"**Return on Equity (ROE):** {roe:.2%}" if roe else "N/A")
            else:
                st.write("No growth metrics available for the selected ticker.")

        elif menu == "Stock Valuation (P/S Ratio)":
            # Stock Valuation logic remains unchanged
            market_cap = float(data.get("MarketCapitalization", 0))
            revenue = float(data.get("RevenueTTM", 0))
            shares_outstanding = float(data.get("SharesOutstanding", 0))

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
            # DCF Model Valuation logic remains unchanged
            pass

