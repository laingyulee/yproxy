import yfinance as yf
from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np

app = FastAPI()

def dataframe_to_json(df: pd.DataFrame):
    """Helper function to convert a Pandas DataFrame to a JSON-serializable list of records."""
    if df.empty:
        return []
    
    # Replace infinity with NaN, then fill all NaN with None for JSON compliance
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # Handle fillna more robustly to prevent "Must specify a fill 'value' or 'method'" error
    try:
        df = df.fillna(value=None)
    except Exception:
        # If fillna fails, we'll handle NaN values column by column
        for col in df.columns:
            try:
                df[col] = df[col].fillna(value=None)
            except Exception:
                # If even column-wise fillna fails, we'll convert to object and replace
                df[col] = df[col].astype(object).replace(np.nan, None)
    
    # Convert any datetime-like columns to string format
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            # NaT values would have been converted to None by fillna.
            # We need to handle the None values before applying strftime.
            df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(x) else None)
    
    # For financial data like income statements, we'll use orient='index' to better preserve
    # the row names (financial metrics) as keys
    if isinstance(df.index, pd.MultiIndex):
        # If there's a MultiIndex, reset it to make it JSON serializable
        df = df.reset_index()
    else:
        # For financial statements, it's often better to convert to dict with index as keys
        # But for API compatibility, we'll still use records format after ensuring proper types
        df = df.reset_index()
    
    # Convert large numbers to strings if they exceed JavaScript number limits
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            # Convert values that exceed safe integer limits in JavaScript to strings
            df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) and (isinstance(x, (int, float)) and (x > 9007199254740991 or x < -9007199254740991)) else x)
    
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
        if not data or data.get('current') is None:
            raise HTTPException(status_code=404, detail=f"No analyst price target data found for ticker '{symbol}'.")
        return dict(data)
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
        # For income statement, sometimes data might be valid but have NaN values
        # Instead of raising 404, we will return the dataframe (possibly empty)
        return dataframe_to_json(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
