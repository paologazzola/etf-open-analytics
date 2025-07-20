from dotenv import load_dotenv
from fastapi import FastAPI, Query
from app.service import get_prediction_data
from fastapi.responses import JSONResponse

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

@app.get("/predict")
def predict(
    isin: str,
    days: int = Query(..., gt=1, description="Minimum number of days to use for the prediction")
):
    print(f"[DEBUG] Received request for ISIN={isin}, days={days}")

    try:
        result = get_prediction_data(isin, days)
        return result
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal error while processing prediction"}
        )
