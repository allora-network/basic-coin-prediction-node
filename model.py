import os
import pickle
from zipfile import ZipFile
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from updater import download_binance_monthly_data, download_binance_daily_data
from config import data_base_path, model_file_path


binance_data_path = os.path.join(data_base_path, "binance/futures-klines")
training_price_data_path = os.path.join(data_base_path, "eth_price_data.csv")


def download_data():
    cm_or_um = "um"
    symbols = ["ETHUSDT"]
    intervals = ["1d"]
    years = ["2020", "2021", "2022", "2023", "2024"]
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    download_path = binance_data_path
    download_binance_monthly_data(
        cm_or_um, symbols, intervals, years, months, download_path
    )
    print(f"Downloaded monthly data to {download_path}.")
    current_datetime = datetime.now()
    current_year = current_datetime.year
    current_month = current_datetime.month
    download_binance_daily_data(
        cm_or_um, symbols, intervals, current_year, current_month, download_path
    )
    print(f"Downloaded daily data to {download_path}.")


def format_data():
    files = sorted([x for x in os.listdir(binance_data_path)])

    # No files to process
    if len(files) == 0:
        return

    price_df = pd.DataFrame()
    for file in files:
        zip_file_path = os.path.join(binance_data_path, file)

        if not zip_file_path.endswith(".zip"):
            continue

        myzip = ZipFile(zip_file_path)
        with myzip.open(myzip.filelist[0]) as f:
            line = f.readline()
            header = 0 if line.decode("utf-8").startswith("open_time") else None
        df = pd.read_csv(myzip.open(myzip.filelist[0]), header=header).iloc[:, :11]
        df.columns = [
            "start_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "end_time",
            "volume_usd",
            "n_trades",
            "taker_volume",
            "taker_volume_usd",
        ]
        df.index = [pd.Timestamp(x + 1, unit="ms") for x in df["end_time"]]
        df.index.name = "date"
        price_df = pd.concat([price_df, df])

    price_df.sort_index().to_csv(training_price_data_path)


def train_model():
    # Load the eth price data
    price_data = pd.read_csv(training_price_data_path)
    df = pd.DataFrame()

    # Convert 'date' to a numerical value (timestamp) we can use for regression
    df["date"] = pd.to_datetime(price_data["date"])
    df["date"] = df["date"].map(pd.Timestamp.timestamp)

    df["price"] = price_data[["open", "close", "high", "low"]].mean(axis=1)

    # Reshape the data to the shape expected by sklearn
    x = df["date"].values.reshape(-1, 1)
    y = df["price"].values.reshape(-1, 1)

    # Split the data into training set and test set
    x_train, _, y_train, _ = train_test_split(x, y, test_size=0.2, random_state=0)

    # Train the model
    model = LinearRegression()
    model.fit(x_train, y_train)

    # create the model's parent directory if it doesn't exist
    os.makedirs(os.path.dirname(model_file_path), exist_ok=True)

    # Save the trained model to a file
    with open(model_file_path, "wb") as f:
        pickle.dump(model, f)

    print(f"Trained model saved to {model_file_path}")
