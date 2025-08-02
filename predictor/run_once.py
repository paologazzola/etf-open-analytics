import argparse
import json
from dotenv import load_dotenv
import os
import sys

# Load .env if present
load_dotenv()

# Add parent dir to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.service import get_prediction_data

def main():
    parser = argparse.ArgumentParser(description="Run prediction once and return JSON output")
    parser.add_argument("--isin", required=True, help="ETF ISIN code")
    parser.add_argument("--days", required=True, type=int, help="Number of days to consider for prediction")

    args = parser.parse_args()

    try:
        result = get_prediction_data(args.isin, args.days)
        print(json.dumps(result, default=str, indent=2))  # `default=str` for date serialization
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
