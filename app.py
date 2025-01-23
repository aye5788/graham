import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Fetch Key Metrics TTM from the API
def fetch_key_metrics_ttm(ticker):
    api_key = "j6kCIBjZa1pHewFjf7XaRDlslDxEFuof"
    url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch Key Metrics TTM. Status code: {response.status_code}")
        return None

# Generate insights using Cohere AI
def generate_cohere_insights(metrics):
    cohere_api_key = "i6rCnd8kHKs3DKmfo2glf48xftmfyOZ9kmuP9Gqc"  # Replace with your Cohere API key
    cohere_endpoint = "https://api.cohere.ai/generate"
    prompt = f"Provide a succinct analysis of the following financial metrics: {metrics}"
    payload = {
        "model": "command-xlarge-nightly",
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.7,
    }
    headers = {"Authorization": f"Bearer {cohere_api_key}"}
    response = requests.post(cohere_endpoint, json=payload, headers=headers)
    if response.status_code == 200:
        try:
            response_json = response.json()
            return response_json.get("generations", [{}])[0].get("text", "No insights generated.")
        except Exception as e:
            st.error(f"Failed to parse Cohere response: {e}")
            return None
    else:
        st.error(f"Failed to generate insights with Cohere. Status code: {response.status_code}")
        return None

# Plot bar charts with color-coded bars
def plot_growth_bars(df):
    if not df.empty:
        for growth_type in df['type'].unique():
            data = df[df['type'] == growth_type]
            plt.figure(figsize=(12, 6))
            colors = ['green' if val > 0 else 'red' for val in data['growthNetIncome'].astype(float)]
            plt.bar(
                data['date'],
                data['growthNetIncome'].astype(float) * 100,
                color=colors,
                edgecolor='black',
                width=0.6,
            )
            plt.title(f"{growth_type} Over Time", fontsize=16, fontweight='bold')
            plt.ylabel("Growth (%)", fontsize=12)
            plt.xlabel("Year", fontsize=12)
            plt.xticks(rotation=45, fontsize=10)
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            st.pyplot(plt)
    else:
        st.warning("No growth data available for visualization.")

# Streamlit App
st.title("DCF Valuation and Key Metrics Analysis")

# User Input
ticker = st.text_input("Enter Stock Ticker:", value="AAPL").upper()

if st.button("Run Analysis"):
    # Fetch Key Metrics TTM
    st.subheader(f"Key Metrics TTM for {ticker}")
    key_metrics = fetch_key_metrics_ttm(ticker)
    if key_metrics:
        key_metrics_data = key_metrics[0]
        st.write("### Key Metrics Summary")
        for key, value in key_metrics_data.items():
            st.write(f"**{key}:** {value}")

        # Generate Cohere AI Insights
        st.subheader("Cohere AI Insights")
        insights = generate_cohere_insights(key_metrics_data)
        if insights:
            st.write(insights)
        else:
            st.error("Failed to generate insights with Cohere.")
    else:
        st.error("No Key Metrics data available for the selected ticker.")

    # Growth Metrics Visualization
    st.subheader(f"Growth Metrics for {ticker}")
    growth_data = process_growth_data(ticker)
    if not growth_data.empty:
        plot_growth_bars(growth_data)
    else:
        st.error("No growth data available for the selected ticker.")

