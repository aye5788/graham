import streamlit as st
import pandas as pd
import requests

# Graham Valuation Function
def graham_valuation(eps, growth_rate, risk_free_rate=4.4):
    intrinsic_value = eps * (8.5 + (2 * growth_rate)) * risk_free_rate / 4.4
    return intrinsic_value

# Function to Fetch Data from Alpha Vantage or Yahoo Finance
def fetch_financial_data(ticker):
    # Alpha Vantage API setup
    api_key = "CLP9IN76G4S8OUXN"
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Debug: Display the response keys and full response
        st.write("Response Keys:", data.keys())
        st.write("API Response:", data)

        # Extract EPS and use QuarterlyEarningsGrowthYOY or PEGRatio for Growth Rate
        eps = data.get("EPS")  # Corrected to use "EPS"
        growth_rate = data.get("QuarterlyEarningsGrowthYOY")  # Use as a proxy for Growth Rate

        # Ensure valid data
        if eps and growth_rate:
            # Convert growth rate from decimal to percentage
            growth_rate = float(growth_rate) * 100
            return {
                "Ticker": ticker,
                "EPS": float(eps),
                "Growth Rate": growth_rate
            }
        else:
            # Handle missing EPS or Growth Rate
            st.error("Required data (EPS or Growth Rate) not found in the API response.")
            return None
    else:
        # Handle API errors
        st.error(f"API request failed with status code: {response.status_code}")
        return None

# Streamlit App
st.title("Graham Valuation Calculator")
st.write("Input a stock ticker to calculate its intrinsic value based on Benjamin Graham's formula.")

# User Input
ticker = st.text_input("Enter Stock Ticker:", value="AAPL").upper()

if st.button("Run Analysis"):
    # Fetch Data
    data = fetch_financial_data(ticker)
    if data:
        # Perform Graham Valuation
        intrinsic_value = graham_valuation(data["EPS"], data["Growth Rate"])
        
        # Display Results
        st.subheader(f"Results for {ticker}")
        st.write(f"**EPS**: {data['EPS']}")
        st.write(f"**Growth Rate**: {data['Growth Rate']}%")
        st.write(f"**Intrinsic Value**: ${intrinsic_value:.2f}")

        # Visualization
        st.bar_chart(pd.DataFrame({
            "Metric": ["EPS", "Growth Rate", "Intrinsic Value"],
            "Value": [data["EPS"], data["Growth Rate"], intrinsic_value]
        }).set_index("Metric"))
    else:
        st.error("Unable to fetch data for the given ticker. Please try another.")
