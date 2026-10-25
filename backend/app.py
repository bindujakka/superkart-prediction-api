import numpy as np
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from pathlib import Path

superkart_api = Flask("superkart_app")

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "superkart_model_v1.joblib"
model = joblib.load(MODEL_PATH)

@superkart_api.get('/')
def home():

    return "Welcome to Superkart "

@superkart_api.post('/v1/predict')
def predict_sales():
    data = request.get_json()
    sample = {
        'Product_Weight': data['Product_Weight'],
        'Product_Sugar_Content': data['Product_Sugar_Content'],
        'Product_Allocated_Area': data['Product_Allocated_Area'],
        'Product_MRP': data['Product_MRP'],
        'Store_Size': data['Store_Size'],
        'Store_Location_City_Type': data['Store_Location_City_Type'],
        'Store_Type': data['Store_Type'],
        'Product_Id_char': data['Product_Id_char'],
        'Store_Age_Years': data['Store_Age_Years'],
        'Product_Type_Category': data['Product_Type_Category']
    }
    # Convert the extracted data into DF
    input_data = pd.DataFrame([sample])

    # Prediction using trained model
    prediction = model.predict(input_data).tolist()[0]
    #Return JSON response
    return jsonify({'Sales': prediction})

@superkart_api.post('/v1/predictbatch')
def predict_batch():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']

    # Read the file into DF
    df_batch = pd.read_csv(file)
    df_batch = df_batch[[
        'Product_Weight', 'Product_Sugar_Content', 'Product_Allocated_Area',
        'Product_MRP', 'Store_Size', 'Store_Location_City_Type',
        'Store_Type', 'Product_Id_char', 'Store_Age_Years', 'Product_Type_Category'
    ]]
    #Model prediction
    predictions = model.predict(df_batch).tolist()
    results = {str(i): pred for i, pred in enumerate(predictions)}
    return jsonify(results)

if __name__ == '__main__':
    superkart_api.run(host='0.0.0.0', port=7860, debug=True)
