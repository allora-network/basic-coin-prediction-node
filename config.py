import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app_base_path = os.getenv("APP_BASE_PATH", default=os.getcwd())
data_base_path = os.path.join(app_base_path, "data")
model_file_path = os.path.join(data_base_path, "model.pkl")

TOKEN = os.getenv("TOKEN").upper()
TRAINING_DAYS = os.getenv("TRAINING_DAYS")
TIMEFRAME = os.getenv("TIMEFRAME")
MODEL = os.getenv("MODEL")
REGION = os.getenv("REGION").lower()
if REGION in ["us", "com", "usa"]:
    REGION = "us"
else:
    REGION = "com"
DATA_PROVIDER = os.getenv("DATA_PROVIDER").lower()
CG_API_KEY = os.getenv("CG_API_KEY", default=None)
