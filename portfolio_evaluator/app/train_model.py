import os
import joblib
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from app.db import load_training_data

load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH", "models/risk_model.pkl")
CHECKPOINT_FILE = os.getenv("CHECKPOINT_FILE", "data/last_training_date.txt")

# === Checkpoint Logic ===
def get_last_training_date() -> str:
    if not os.path.exists(CHECKPOINT_FILE):
        return (datetime.today().replace(year=datetime.today().year - 3)).date().isoformat()
    with open(CHECKPOINT_FILE) as f:
        return f.read().strip()

def set_last_training_date():
    today = datetime.today().date().isoformat()
    os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)
    with open(CHECKPOINT_FILE, "w") as f:
        f.write(today)

# === Model Training ===
def train_and_save_model():
    since = get_last_training_date()
    print(f"[INFO] Loading training data since {since}...")
    df = pd.DataFrame(load_training_data(since))

    if df.empty:
        print("[WARNING] No new data available for training.")
        return

    X = df.drop("risk", axis=1)
    y = df["risk"]

    numeric_features = ["volatility"]
    categorical_features = ["asset_class", "region", "replication_method"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features),
            ("cat", OneHotEncoder(), categorical_features),
        ]
    )

    model = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    model.fit(X, y)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    set_last_training_date()
    print(f"[INFO] Model trained and saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_and_save_model()
