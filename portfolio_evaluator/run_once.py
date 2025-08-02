import sys
import os

# Ensure app is in the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.train_model import train_and_save_model

if __name__ == "__main__":
    print("[INFO] Starting one-time model training...")
    try:
        train_and_save_model()
        print("[INFO] Training completed successfully.")
    except Exception as e:
        print(f"[ERROR] Training failed: {e}")
