import streamlit as st
import requests

# Fetch Data from Alpha Vantage
def fetch_financial_data(ticker):
    api_key = "CLP9IN76G4S8OUXN"
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API request failed with status code: {response.status_code}")
        return None

# Calculate 1-Year Price Change Using Alpha Vantage Data
def calculate_price_change(data):
    try:
        high = float(data.get("52WeekHigh", 0))
        low = float(data.get("52WeekLow", 0))
        if high > 0 and low > 0:
            return ((high - low) / low) * 100
        else:
            return None
    except Exception:
        return None

# Estimate Time to Profitability
def estimate_time_to_profitability(data):
    try:
        profit_margin = float(data.get("ProfitMargin", 0))  # Current profit margin
        revenue_growth = float(data.get("QuarterlyRevenueGrowthYOY", 0))  # Revenue growth (YOY)
        
        if profit_margin > 0:
            return "Already Profitable"
        elif profit_margin < 0 and revenue_growth > 0:
            # Time to profitability (in quarters)
            ttp_quarters = abs(profit_margin) / revenue_growth
            ttp_years = ttp_quarters / 4  # Convert to years
            return round(ttp_years, 2)
        else:
            return None  # Insufficient data
    except Exception:
        return None

# Calculate Graham Valuation
def calculate_graham_valuation(data):
    try:
        eps = float(data.get("EPS", 0))
        growth_rate = float(data.get("QuarterlyRevenueGrowthYOY", 0)) * 100  # Convert to percentage
        bond_yield = 4.4  # Assume 4.4% as default AAA bond yield (can be adjusted)

        if eps > 0 and growth_rate > 0:
            intrinsic_value = eps * (8.5 + 2 * growth_rate) * (4.4 / bond_yield)
            return round(intrinsic_value, 2)
        else:
            return None
    except Exception:
        return None

# Streamlit App
st.title("Enhanced Stock Analysis Tool")

# Sidebar Menu
menu = st.sidebar.radio("Select Analysis Type", ["Graham Valuation", "Growth Stock Analysis"])

# User Input
ticker = st.text_input("Enter Stock Ticker:", value="AAPL").upper()

if st.button("Run Analysis"):
    # Fetch data
    data = fetch_financial_data(ticker)

    if data:
        if menu == "Growth Stock Analysis":
            # Extract relevant metrics
            revenue_growth = data.get("QuarterlyRevenueGrowthYOY")
            market_cap = data.get("MarketCapitalization")
            price_change_1y = calculate_price_change(data)
            ttp = estimate_time_to_profitability(data)

            # Format and handle missing data
            revenue_growth_display = f"{float(revenue_growth) * 100:.1f}%" if revenue_growth else "N/A"
            market_cap_display = f"${float(market_cap) / 1e9:.2f}B" if market_cap else "N/A"
            price_change_display = f"{price_change_1y:.2f}%" if price_change_1y is not None else "N/A"
            ttp_display = ttp if ttp else "N/A"

            # Display Results
            st.subheader(f"Growth Stock Analysis for {ticker}")
            st.write(f"**Quarterly Revenue Growth (YOY)**: {revenue_growth_display}")
            st.write(f"**Market Capitalization**: {market_cap_display}")
            st.write(f"**1-Year Price Change**: {price_change_display}")
            st.write(f"**Estimated Time to Profitability**: {ttp_display}")

            # Evidence Section
            st.write("### Evidence:")
            st.write(f"- **Revenue Growth**: A growth rate of {revenue_growth_display} "
                     f"{'indicates strong growth potential' if revenue_growth and float(revenue_growth) * 100 > 20 else 'indicates moderate growth potential'}.")
            st.write(f"- **Market Capitalization**: The company has a market cap of {market_cap_display}, "
                     f"{'classifying it as a large-cap stock' if market_cap and float(market_cap) > 10e9 else 'placing it in the mid/small-cap category'}.")
            st.write(f"- **Price Performance**: Over the past year, the price has changed by {price_change_display}, "
                     f"{'indicating strong momentum' if price_change_1y and price_change_1y > 20 else 'indicating moderate performance'}.")
            st.write(f"- **Profitability**: {ttp_display}.")

        elif menu == "Graham Valuation":
            # Calculate Graham Valuation
            graham_valuation = calculate_graham_valuation(data)

            # Display Results
            st.subheader(f"Graham Valuation Analysis for {ticker}")
            if graham_valuation:
                st.write(f"**Intrinsic Value (Graham Valuation)**: ${graham_valuation}")
            else:
                st.write("Graham Valuation could not be calculated. Please ensure EPS and growth rate data are available.")
