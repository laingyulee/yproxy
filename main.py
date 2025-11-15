import yfinance as yf
from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np

app = FastAPI()

def dataframe_to_json(df: pd.DataFrame):
    """Helper function to convert a Pandas DataFrame to a JSON-serializable list of records."""
    if df.empty:
        return []
    df = df.reset_index()
    # Replace infinity with NaN, then fill all NaN with None for JSON compliance
    df = df.replace([np.inf, -np.inf], np.nan).fillna(None)
    # Convert any datetime-like columns to string format
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df.to_dict('records')

@app.get("/")
def read_root():
    return {"message": "yfinance API Proxy is running. Use /docs for API documentation."}

@app.get("/ticker/{symbol}/info")
def get_ticker_info(symbol: str):
    """
    Get comprehensive information for a given stock ticker.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        # A heuristic to check if the ticker is valid and has data
        if not info or info.get('regularMarketPrice') is None:
            raise HTTPException(status_code=404, detail=f"Ticker symbol '{symbol}' not found or no data available.")
        return info
    except Exception as e:
        # Catching broad exceptions to handle various yfinance or network errors
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching data for {symbol}: {str(e)}")

@app.get("/ticker/{symbol}/history")
def get_ticker_history(symbol: str, period: str = "1mo", interval: str = "1d"):
    """
    Get historical market data for a given stock ticker.
    
    - **period**: Data period to download (e.g., 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    - **interval**: Data interval (e.g., 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No historical data found for ticker '{symbol}' with the given parameters.")
        return dataframe_to_json(hist)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching history for {symbol}: {str(e)}")

@app.get("/ticker/{symbol}/analyst-price-targets")
def get_analyst_price_targets(symbol: str):
    """
    Get analyst price targets for a given stock ticker.
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.analyst_price_targets
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No analyst price target data found for ticker '{symbol}'.")
        return dataframe_to_json(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/ticker/{symbol}/fast-info")
def get_fast_info(symbol: str):
    """
    Get fast, basic info for a given stock ticker.
    """
    try:
        ticker = yf.Ticker(symbol)
        # .fast_info returns a LazyDict which is directly JSON serializable
        data = ticker.fast_info
        if not data:
            raise HTTPException(status_code=404, detail=f"No fast_info data found for ticker '{symbol}'.")
        return dict(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/ticker/{symbol}/income-stmt")
def get_income_stmt(symbol: str):
    """
    Get the income statement for a given stock ticker.
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.income_stmt
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No income statement data found for ticker '{symbol}'.")
        return dataframe_to_json(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
