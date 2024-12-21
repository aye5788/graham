import yfinance as yf
import streamlit as st
import requests

# Fetch Data from Alpha Vantage
def fetch_financial_data(ticker):
    api_key = "CLP9IN76G4S8OUXN"
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

# Fetch Peer Data from yfinance
def fetch_yfinance_data(ticker):
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
        historical = stock.history(period="1y")
        return {
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "peers": info.get("longBusinessSummary", "No peer data available"),
            "price_change_1y": (historical["Close"][-1] - historical["Close"][0]) / historical["Close"][0] * 100,
        }
    except Exception as e:
        return {"error": str(e)}

# Streamlit App
st.title("Enhanced Stock Analysis Tool")
menu = st.sidebar.radio("Select Analysis Type", ["Graham Valuation", "Growth Stock Analysis"])
ticker = st.text_input("Enter Stock Ticker:", value="AAPL").upper()

if st.button("Run Analysis"):
    data = fetch_financial_data(ticker)
    yf_data = fetch_yfinance_data(ticker)

    if data and yf_data:
        if menu == "Growth Stock Analysis":
            # Extract relevant metrics
            revenue_growth = float(data.get("QuarterlyRevenueGrowthYOY", 0)) * 100
            peg_ratio = data.get("PEGRatio", "N/A")
            market_cap = float(data.get("MarketCapitalization", 0)) / 1e9
            price_change_1y = yf_data.get("price_change_1y", "N/A")
            sector = yf_data.get("sector", "Unknown")
            industry = yf_data.get("industry", "Unknown")
            peers = yf_data.get("peers", "N/A")

            # Display Results
            st.subheader(f"Growth Stock Analysis for {ticker}")
            st.write(f"**Quarterly Revenue Growth (YOY)**: {revenue_growth:.1f}%")
            st.write(f"**PEG Ratio**: {peg_ratio}")
            st.write(f"**Market Capitalization**: ${market_cap:.2f}B")
            st.write(f"**1-Year Price Change**: {price_change_1y:.2f}%")
            st.write(f"**Sector**: {sector}")
            st.write(f"**Industry**: {industry}")

            # Evidence Section
            st.write("### Evidence:")
            st.write(f"- **Revenue Growth**: A growth rate of {revenue_growth:.1f}% "
                     f"compared to the sector average demonstrates {'strong' if revenue_growth > 20 else 'moderate'} potential.")
            st.write(f"- **PEG Ratio**: PEG ratio of {peg_ratio} {'suggests undervaluation' if peg_ratio != 'N/A' and float(peg_ratio) < 1 else 'may indicate overvaluation'}.")
            st.write(f"- **Market Capitalization**: With a market cap of ${market_cap:.2f}B, "
                     f"{ticker} is classified as a {'large-cap' if market_cap > 10 else 'mid/small-cap'} stock.")
            st.write(f"- **Sector and Industry**: The company operates in the {sector} sector, specifically the {industry} industry.")
            st.write(f"- **Price Performance**: Over the past year, the stock price has changed by {price_change_1y:.2f}%, "
                     f"indicating {'strong momentum' if price_change_1y > 20 else 'moderate performance'}.")
