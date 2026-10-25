import streamlit as st
import pandas as pd
import requests
import os


def get_backend_url():
    env_url = os.getenv("BACKEND_URL")
    if env_url:
        return env_url.rstrip("/")
    if os.path.exists("/.dockerenv"):
        return "http://backend:7860"
    return "http://127.0.0.1:7860"


BACKEND_URL = get_backend_url()



st.title("🛒 SuperKart Sales Forecasting Dashboard")
st.write("Interactive interface to estimate sales revenue for product-store combinations.")
tabs = st.tabs(["Single Prediction", "Batch Upload"])

with tabs[0]:
    st.header("Single Product-Store Feature Entry")
    col1, col2 = st.columns(2)
    
    with col1:
        product_weight = st.number_input("Product Weight (kg)", min_value=1.0, max_value=30.0, value=12.5)
        product_sugar = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        allocated_area = st.number_input("Display Allocated Area Ratio", min_value=0.0, max_value=0.5, value=0.05, step=0.01)
        product_mrp = st.number_input("Product Maximum Retail Price (MRP)", min_value=10.0, max_value=500.0, value=140.0)
        product_id_char = st.selectbox("Product Category Prefix (ID)", ["FD", "NC", "DR"])
        
    with col2:
        store_size = st.selectbox("Store Size", ["Medium", "High", "Small"])
        store_city_type = st.selectbox("Store Location City Type", ["Tier 2", "Tier 1", "Tier 3"])
        store_type = st.selectbox("Store Type Format", ["Supermarket Type2", "Supermarket Type1", "Departmental Store", "Food Mart"])
        store_age = st.number_input("Store Age (Years)", min_value=1, max_value=100, value=16)
        product_category = st.selectbox("Broad Product Category Group", ["Perishables", "Non Perishables", "Drinks", "Non Consumables"])

    if st.button("Predict Sales Revenue"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar,
            "Product_Allocated_Area": allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": int(store_age),
            "Product_Type_Category": product_category
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                predicted_sales = result.get("Sales", 0.0)
                st.success(f"💰 Predicted Store Revenue: **${predicted_sales:,.2f}**")
            else:
                st.error(f"Backend API Error: {response.text}")
        except Exception as e:
            st.error(f"Unable to establish connection with backend: {e}")

with tabs[1]:
    st.header("Bulk File Upload (.csv)")
    st.write("Upload a batch CSV file with transaction records to predict sales across multiple product entries simultaneously.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        df_input = pd.read_csv(uploaded_file)
        st.write("Uploaded File Preview:")
        st.dataframe(df_input.head())
        
        if st.button("Run Batch Predictions"):
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}
            try:
                response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files, timeout=30)
                if response.status_code == 200:
                    predictions = response.json()
                    df_results = df_input.copy()
                    df_results['Predicted_Sales'] = [predictions[str(i)] for i in range(len(df_input))]
                    st.success("Batch Processing Complete!")
                    st.dataframe(df_results)
                    
                    # Download Link
                    csv_downloader = df_results.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Forecasted Results", data=csv_downloader, file_name="superkart_predictions.csv", mime="text/csv")
                else:
                    st.error(f"Error processing batch: {response.text}")
            except Exception as e:
                st.error(f"Unable to connect to service: {e}")
