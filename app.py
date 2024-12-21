import streamlit as st
import requests

# Graham Valuation Formula
def graham_valuation(eps, growth_rate, risk_free_rate=4.4):
    intrinsic_value = eps * (8.5 + (2 * growth_rate)) * risk_free_rate / 4.4
    return intrinsic_value

# Fetch Data Function
def fetch_financial_data(ticker):
    api_key = "CLP9IN76G4S8OUXN"  # Replace with your Alpha Vantage API Key
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API request failed with status code: {response.status_code}")
        return None

# Streamlit App
st.title("Stock Analysis Tool")

# Sidebar Menu
menu = st.sidebar.radio("Select Analysis Type", ["Graham Valuation", "Growth Stock Analysis"])

# User Input
ticker = st.text_input("Enter Stock Ticker:", value="AAPL").upper()

if st.button("Run Analysis"):
    # Fetch data
    data = fetch_financial_data(ticker)

    if data:
        if menu == "Graham Valuation":
            # Perform Graham Valuation Analysis
            eps = data.get("EPS")
            growth_rate = data.get("QuarterlyEarningsGrowthYOY")

            if eps and growth_rate:
                growth_rate = float(growth_rate) * 100  # Convert to percentage
                intrinsic_value = graham_valuation(float(eps), growth_rate)

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

        elif menu == "Growth Stock Analysis":
            # Perform Growth Stock Analysis
            revenue_growth = data.get("QuarterlyRevenueGrowthYOY")
            peg_ratio = data.get("PEGRatio")
            market_cap = data.get("MarketCapitalization")

            if revenue_growth:
                revenue_growth = float(revenue_growth) * 100  # Convert to percentage

            # Display Results
            st.subheader(f"Growth Stock Analysis for {ticker}")
            st.write(f"**Quarterly Revenue Growth (YOY)**: {revenue_growth:.1f}%" if revenue_growth else "N/A")
            st.write(f"**PEG Ratio**: {peg_ratio or 'N/A'}")
            st.write(f"**Market Capitalization**: ${int(market_cap) / 1e9:.2f}B" if market_cap else "N/A")

            # Explain the verdict
            st.write("### Evidence:")
            if revenue_growth:
                st.write(f"- **Quarterly Revenue Growth (YOY)**: A growth rate of {revenue_growth:.1f}% "
                         f"indicates {('strong' if revenue_growth > 20 else 'moderate')} growth potential.")
            if peg_ratio:
                st.write(f"- **PEG Ratio**: The PEG ratio of {peg_ratio} measures the price-to-earnings growth, "
                         f"indicating valuation relative to growth potential.")
            if market_cap:
                st.write(f"- **Market Capitalization**: The company has a market cap of ${int(market_cap) / 1e9:.2f}B, "
                         f"which places it in the {('large-cap' if float(market_cap) > 10e9 else 'mid/small-cap')} category.")

            # Provide Overall Verdict
            if revenue_growth and revenue_growth > 20:
                st.success("This stock demonstrates strong revenue growth. It may qualify as a growth stock.")
            else:
                st.warning("Revenue growth is moderate. This stock may not qualify as a strong growth stock.")
    else:
        st.error("Unable to fetch data. Please try another ticker.")

