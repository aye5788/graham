import streamlit as st
import requests

# Graham Valuation Formula
def graham_valuation(eps, growth_rate, risk_free_rate=4.4):
    intrinsic_value = eps * (8.5 + (2 * growth_rate)) * risk_free_rate / 4.4
    return intrinsic_value

# Fetch Data Function
def fetch_financial_data(ticker):
    # Alpha Vantage API setup
    api_key = "CLP9IN76G4S8OUXN"  # Replace with your API key
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Extract EPS and Growth Rate
        eps = data.get("EPS")  # Use the "EPS" key from the API response
        growth_rate = data.get("QuarterlyEarningsGrowthYOY")  # Use as proxy for Growth Rate

        # Ensure valid data
        if eps and growth_rate:
            growth_rate = float(growth_rate) * 100  # Convert to percentage
            return {
                "Ticker": ticker,
                "EPS": float(eps),
                "Growth Rate": growth_rate
            }
        else:
            st.error("Required data (EPS or Growth Rate) not found in the API response.")
            return None
    else:
        st.error(f"API request failed with status code: {response.status_code}")
        return None

# Streamlit App
st.title("Graham Valuation Calculator")
st.write("Input a stock ticker to calculate its intrinsic value based on Benjamin Graham's formula.")

# User Input
ticker = st.text_input("Enter Stock Ticker:", value="AAPL").upper()

if st.button("Run Analysis"):
    # Fetch data
    data = fetch_financial_data(ticker)

    if data:
        # Perform valuation
        intrinsic_value = graham_valuation(data["EPS"], data["Growth Rate"])

        # Display results
        st.subheader(f"Results for {data['Ticker']}")
        st.write(f"**EPS**: {data['EPS']}")
        st.write(f"**Growth Rate**: {data['Growth Rate']:.1f}%")
        st.write(f"**Intrinsic Value**: ${intrinsic_value:.2f}")
