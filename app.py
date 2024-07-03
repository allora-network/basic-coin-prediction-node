import json
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from flask import Flask, jsonify, Response
from model import download_data, format_data, train_model
from config import model_file_path

app = Flask(__name__)


def update_data():
    """Download price data, format data and train model."""
    download_data()
    format_data()
    train_model()


def get_sol_inference():
    """Load model and predict current price."""
    with open(model_file_path, "rb") as f:
        loaded_model = pickle.load(f)

    now_timestamp = pd.Timestamp(datetime.now()).timestamp()
    X_new = np.array([now_timestamp]).reshape(-1, 1)
    current_price_pred = loaded_model.predict(X_new)

    return current_price_pred[0][0]


@app.route("/inference/<string:token>")
def generate_inference(token):
    """Generate inference for given token."""
    if not token or token != "SOL":
        error_msg = "Token is required" if not token else "Token not supported"
        return Response(json.dumps({"error": error_msg}), status=400, mimetype='application/json')

    try:
        inference = get_sol_inference()
        return Response(str(inference), status=200)
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


@app.route("/update")
def update():
    """Update data and return status."""
    try:
        update_data()
        return "0"
    except Exception:
        return "1"


if __name__ == "__main__":
    update_data()
    app.run(host="0.0.0.0", port=8000)
