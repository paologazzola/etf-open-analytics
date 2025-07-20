from typing import List
import numpy as np
from sklearn.linear_model import LinearRegression

def predict_next_log_return(log_returns: List[float]) -> float:
    """
    Predicts the next log return using a linear regression
    based on the historical log return series.
    """
    if len(log_returns) < 2:
        raise ValueError("At least 2 log return values are required to make a prediction.")

    # Independent variable: time index (0, 1, 2, ..., n-1)
    X = np.arange(len(log_returns)).reshape(-1, 1)
    # Dependent variable: log_return values
    y = np.array(log_returns)

    model = LinearRegression()
    model.fit(X, y)

    # Predict the next value (index n)
    next_index = np.array([[len(log_returns)]])
    predicted_log_return = model.predict(next_index)[0]

    return predicted_log_return
