import streamlit as st
import requests

# Fetch Data from Alpha Vantage
def fetch_financial_data(ticker):
    api_key = "CLP9IN76G4S8OUXN"  # Replace with your API key
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
            peg_ratio = data.get("PEGRatio")
            market_cap = data.get("MarketCapitalization")
            price_change_1y = calculate_price_change(data)

            # Format and handle missing data
            revenue_growth_display = f"{float(revenue_growth) * 100:.1f}%" if revenue_growth else "N/A"
            peg_ratio_display = peg_ratio or "N/A"
            market_cap_display = f"${float(market_cap) / 1e9:.2f}B" if market_cap else "N/A"
            price_change_display = f"{price_change_1y:.2f}%" if price_change_1y is not None else "N/A"

            # Display Results
            st.subheader(f"Growth Stock Analysis for {ticker}")
            st.write(f"**Quarterly Revenue Growth (YOY)**: {revenue_growth_display}")
            st.write(f"**PEG Ratio**: {peg_ratio_display}")
            st.write(f"**Market Capitalization**: {market_cap_display}")
            st.write(f"**1-Year Price Change**: {price_change_display}")

            # Evidence Section
            st.write("### Evidence:")
            st.write(f"- **Revenue Growth**: A growth rate of {revenue_growth_display} "
                     f"{'indicates strong growth potential' if revenue_growth and float(revenue_growth) * 100 > 20 else 'indicates moderate growth potential'}.")
            st.write(f"- **PEG Ratio**: The PEG ratio of {peg_ratio_display} {'suggests undervaluation' if peg_ratio and float(peg_ratio) < 1 else 'may indicate overvaluation'}.")
            st.write(f"- **Market Capitalization**: The company has a market cap of {market_cap_display}, "
                     f"{'classifying it as a large-cap stock' if market_cap and float(market_cap) > 10e9 else 'placing it in the mid/small-cap category'}.")
            st.write(f"- **Price Performance**: Over the past year, the price has changed by {price_change_display}, "
                     f"{'indicating strong momentum' if price_change_1y and price_change_1y > 20 else 'indicating moderate performance'}.")

        elif menu == "Graham Valuation":
            # Perform Graham Valuation Analysis
            eps = data.get("EPS")
            growth_rate = data.get("QuarterlyEarningsGrowthYOY")

            if eps and growth_rate:
                growth_rate = float(growth_rate) * 100  # Convert to percentage
                intrinsic_value = eps * (8.5 + (2 * growth_rate)) * 4.4 / 4.4

                # Display Results
                st.subheader(f"Graham Valuation Results for {ticker}")
                st.write(f"**EPS**: {eps}")
                st.write(f"**Growth Rate**: {growth_rate:.1f}%")
                st.write(f"**Intrinsic Value**: ${intrinsic_value:.2f}")

                # Explain the verdict
                st.write("### Evidence:")
                st.write(f"- **EPS**: The Earnings Per Share (EPS) indicates the company's profitability. For {ticker}, the EPS is {eps}.")
                st.write(f"- **Growth Rate**: The growth rate of {growth_rate:.1f}% reflects the company's potential for future earnings.")
                st.write(f"- **Formula**: The intrinsic value is calculated using Benjamin Graham's formula: "
                         f"`Intrinsic Value = EPS * (8.5 + 2 * Growth Rate) * Risk-Free Rate / 4.4`.")
            else:
                st.error("Graham Valuation cannot be applied. EPS or Growth Rate data is missing.")
