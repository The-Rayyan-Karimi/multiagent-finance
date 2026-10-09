import yfinance as yf
from typing import Dict, Any

def get_stock_info(ticker: str) -> Dict[str, Any]:
    """
    Fetches the current stock price and basic company information.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT').
        
    Returns:
        dict: A dictionary containing current price, currency, company name, and sector.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # yfinance can sometimes have missing fields, so we use .get() safely
        return {
            "symbol": ticker.upper(),
            "company_name": info.get("shortName", "Unknown"),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
            "currency": info.get("currency", "USD"),
            "sector": info.get("sector", "Unknown"),
            "market_cap": info.get("marketCap")
        }
    except Exception as e:
        return {"error": f"Failed to fetch data for {ticker}. It might be invalid. Details: {str(e)}"}

def get_historical_prices(ticker: str, period: str = "1mo") -> Dict[str, Any]:
    """
    Fetches historical closing prices for a stock.
    
    Args:
        ticker (str): The stock ticker symbol.
        period (str): The time period (e.g., '1d', '5d', '1mo', '3mo', '1y').
        
    Returns:
        dict: A dictionary of dates and their closing prices.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            return {"error": f"No historical data found for {ticker}."}
            
        # Convert pandas series to a simple dictionary { "YYYY-MM-DD": Price }
        closing_prices = {
            date.strftime('%Y-%m-%d'): round(price, 2) 
            for date, price in hist['Close'].items()
        }
        
        return {
            "symbol": ticker.upper(),
            "period": period,
            "closing_prices": closing_prices
        }
    except Exception as e:
        return {"error": f"Failed to fetch history for {ticker}: {str(e)}"}
