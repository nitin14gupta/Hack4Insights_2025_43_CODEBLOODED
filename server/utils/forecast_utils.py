from typing import List, Dict, Any
import math

def calculate_linear_forecast(historical_data: List[float], periods_to_forecast: int = 3) -> Dict[str, Any]:
    """
    Calculates a linear forecast based on historical data points.
    Returns the regression line points for historical data and future predictions.
    Uses simple Least Squares method.
    """
    n = len(historical_data)
    if n < 2:
        return {
            "historical_trend": historical_data,
            "forecast": [historical_data[0]] * periods_to_forecast if n==1 else [],
            "slope": 0,
            "growth_rate": 0
        }

    # X values are just time indices 0, 1, 2...
    x = list(range(n))
    y = historical_data

    # Calculate means
    x_mean = sum(x) / n
    y_mean = sum(y) / n

    # Calculate slope (m) and intercept (b)
    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    denominator = sum((xi - x_mean) ** 2 for xi in x)

    if denominator == 0:
        m = 0
    else:
        m = numerator / denominator

    b = y_mean - (m * x_mean)

    # Generate trend line for historical data (smoothing)
    historical_trend = [m * xi + b for xi in x]

    # Generate forecast
    forecast = []
    for i in range(1, periods_to_forecast + 1):
        future_x = n - 1 + i
        forecast.append(m * future_x + b)

    # Calculate Growth Rate (CAGR-ish based on slope relative to mean)
    growth_rate = (m / y_mean) if y_mean != 0 else 0

    return {
        "historical_trend": historical_trend,
        "forecast": forecast,
        "slope": m,
        "intercept": b,
        "growth_rate": growth_rate
    }
