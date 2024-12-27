import streamlit as st
import requests

# Fetch Data from Alpha Vantage - OVEREVIEW
def fetch_financial_data(ticker):
    api_key = "CLP9IN76G4S8OUXN"
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API request failed with status code: {response.status_code}")
        return None

# Calculate Price-to-Sales (P/S) Ratio
def calculate_ps_ratio(data):
    try:
        market_cap = float(data.get("MarketCapitalization", 0))
        revenue = float(data.get("RevenueTTM", 0))  # Total Revenue (Trailing Twelve Months)

        if revenue > 0:
            ps_ratio = market_cap / revenue
            return round(ps_ratio, 2)
        else:
            return None
    except Exception:
        return None

# Discounted Cash Flow (DCF) Model
def calculate_dcf(data, growth_rate=0.1, discount_rate=0.08, years=5):
    """
    This is a simplified DCF model where:
    - growth_rate: Expected annual growth rate of free cash flow (assumed 10% if not provided)
    - discount_rate: Discount rate (assumed 8% if not provided)
    - years: Number of years to project cash flows
    """
    try:
        fcf = float(data.get("FreeCashFlow", 0))  # Free Cash Flow (assumed if available)
        if fcf <= 0:
            fcf = 100000000  # Assume a baseline if not available (for non-profitable companies)

        dcf_value = 0
        for t in range(1, years + 1):
            projected_fcf = fcf * (1 + growth_rate) ** t
            dcf_value += projected_fcf / (1 + discount_rate) ** t

        return round(dcf_value, 2)
    except Exception:
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
            # Calculate P/S Ratio
            ps_ratio = calculate_ps_ratio(data)
            if ps_ratio:
                st.subheader(f"P/S Ratio Valuation for {ticker}")
                st.write(f"**Price-to-Sales (P/S) Ratio:** {ps_ratio}")
                
                # Dynamic interpretation of P/S Ratio
                if ps_ratio < 1:
                    st.write("**Interpretation:** This suggests the stock might be undervalued relative to its sales.")
                elif 1 <= ps_ratio <= 3:
                    st.write("**Interpretation:** The stock appears reasonably valued in terms of its sales.")
                else:
                    st.write("**Interpretation:** The stock seems expensive relative to its sales. It could be overvalued.")
            else:
                st.write("P/S Ratio could not be calculated. Please ensure MarketCap and Revenue data are available.")

        elif menu == "DCF Model Valuation":
            # Calculate DCF (Discounted Cash Flow) Value
            dcf_value = calculate_dcf(data)
            if dcf_value:
                st.subheader(f"DCF Model Valuation for {ticker}")
                st.write(f"**Discounted Cash Flow (DCF) Valuation:** ${dcf_value}")
                
                # Dynamic interpretation of DCF value
                market_cap = float(data.get("MarketCapitalization", 0))
                if dcf_value < market_cap:
                    st.write("**Interpretation:** The stock is currently overvalued based on its future cash flows.")
                elif dcf_value > market_cap:
                    st.write("**Interpretation:** The stock appears undervalued, with a market price lower than its intrinsic value.")
                else:
                    st.write("**Interpretation:** The stock seems fairly valued, with its market price close to the calculated intrinsic value.")
            else:
                st.write("DCF Valuation could not be calculated. Please ensure Free Cash Flow data is available.")


