import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Fetch DCF Valuation from FMP DCF Reports API
def fetch_dcf_valuation(ticker):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"  # FMP API Key
    url = f"https://financialmodelingprep.com/api/v3/discounted-cash-flow/{ticker}?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                dcf_value = data[0].get("dcf", "N/A")
                stock_price = data[0].get("Stock Price", "N/A")
                date = data[0].get("date", "N/A")
                return {"DCF Value": dcf_value, "Stock Price": stock_price, "Valuation Date": date}
            else:
                st.error("Unexpected response structure. DCF data not available.")
                return None
        except Exception as e:
            st.error(f"Error parsing DCF data: {e}")
            return None
    else:
        st.error(f"Failed to fetch DCF valuation. Status code: {response.status_code}")
        return None

# Fetch Financial Growth Data
def fetch_financial_growth_data(ticker):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"  # FMP API Key
    url = f"https://financialmodelingprep.com/api/v3/financial-growth/{ticker}?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error(f"Failed to fetch financial growth data. Status code: {response.status_code}")
        return None

# Plot Growth Metrics
def plot_growth_metrics(growth_data):
    if growth_data:
        # Convert to DataFrame
        df = pd.DataFrame(growth_data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Select metrics for visualization
        metrics = {
            "Cashflow Growth": "freeCashFlowGrowth",
            "Income Growth": "netIncomeGrowth",
            "Balance Sheet Growth": "totalAssetsGrowth",
            "Financial Growth": "totalEquityGrowth"
        }

        for title, metric in metrics.items():
            if metric in df.columns and not df[metric].isnull().all():
                st.write(f"### {title}")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(df.index, df[metric].astype(float) * 100, marker='o', label=title)
                ax.set_title(f"{title} Over Time", fontsize=16)
                ax.set_ylabel("Growth (%)", fontsize=12)
                ax.set_xlabel("Date", fontsize=12)
                ax.grid(True)
                ax.legend()
                st.pyplot(fig)
            else:
                st.warning(f"{title} data not available.")

# Streamlit App
st.title("DCF Analysis and Growth Metrics Visualization")

# User Input
ticker = st.text_input("Enter Stock Ticker:", value="AAPL").upper()

if st.button("Run Analysis"):
    # Fetch and Display DCF Valuation
    dcf_data = fetch_dcf_valuation(ticker)
    if dcf_data:
        st.subheader(f"DCF Model Valuation for {ticker}")
        st.write("### Valuation Summary")
        st.write(f"**Discounted Cash Flow (DCF) Value:** ${dcf_data['DCF Value']}")
        st.write(f"**Stock Price:** ${dcf_data['Stock Price']}")
        st.write(f"**Valuation Date:** {dcf_data['Valuation Date']}")

    # Fetch and Display Growth Metrics
    growth_data = fetch_financial_growth_data(ticker)
    if growth_data:
        st.subheader(f"Growth Metrics for {ticker}")
        plot_growth_metrics(growth_data)
