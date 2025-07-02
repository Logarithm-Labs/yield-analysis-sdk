import math
from typing import List, Tuple

from .type import PerformanceAnalysis, SharePriceHistory
from .exceptions import DataError

def analyze_yield_with_daily_share_price(
    share_price_history: SharePriceHistory, risk_free_rate: float = 0.05
) -> PerformanceAnalysis:
    """
    Analyze yield metrics from daily share price data and return essential metrics for allocation decisions.

    Args:
        share_price_history: SharePriceHistory object containing daily share prices
        risk_free_rate: Annual risk-free rate (default 0.05 = 5% for current market conditions)

    Returns:
        PerformanceAnalysis object containing essential yield and risk metrics for allocation decisions
    """

    daily_share_price: List[Tuple[int, float]] = share_price_history.price_history

    if not daily_share_price or len(daily_share_price) < 2:
        raise DataError("At least 2 daily share prices are required for analysis")

    # sort daily_share_price by timestamp in ascending order
    daily_share_price.sort(key=lambda x: x[0])
    # extract price from daily_share_price
    prices: list[float] = [price for timestamp, price in daily_share_price]

    # Calculate daily returns
    daily_returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] > 0:  # Avoid division by zero
            daily_return = (prices[i] - prices[i - 1]) / prices[i - 1]
            daily_returns.append(daily_return)

    # Calculate core APY metrics (7d, 30d, and 90d are most important for allocation decisions)
    apy_7d = _calculate_apy(prices, 7)
    apy_30d = _calculate_apy(prices, 30)
    apy_90d = _calculate_apy(prices, 90)

    # Calculate essential risk metrics
    volatility_30d = _calculate_volatility(daily_returns, 30)
    max_drawdown = _calculate_max_drawdown(prices)

    # Calculate Sharpe ratio (mandatory for allocation decisions)
    sharpe_ratio = _calculate_sharpe_ratio(daily_returns, risk_free_rate)

    # Create PerformanceAnalysis object
    performance_analysis = PerformanceAnalysis(
        apy_7d=apy_7d,
        apy_30d=apy_30d,
        apy_90d=apy_90d,
        volatility_30d=volatility_30d,
        max_drawdown=max_drawdown,
        sharpe_ratio=sharpe_ratio,
        current_price=prices[-1],
        analysis_period_days=len(prices),
    )

    return performance_analysis


def _calculate_apy(prices: List[float], days: int) -> float:
    """Calculate APY for a given period."""
    if len(prices) < days:
        return 0.0

    start_price = prices[-days]
    end_price = prices[-1]

    if start_price <= 0:
        return 0.0

    # Calculate total return
    total_return = (end_price - start_price) / start_price

    # Convert to APY (annualized)
    apy: float = (1 + total_return) ** (365 / days) - 1

    return apy * 100  # Convert to percentage


def _calculate_volatility(returns: List[float], days: int) -> float:
    """Calculate volatility (standard deviation of returns) for a given period."""
    if len(returns) < days:
        return 0.0

    period_returns = returns[-days:]
    mean_return = sum(period_returns) / len(period_returns)

    # Calculate sample variance (using n-1 for sample standard deviation)
    variance = sum((r - mean_return) ** 2 for r in period_returns) / (
        len(period_returns) - 1
    )
    volatility = math.sqrt(variance)

    # Annualize volatility (assuming daily returns)
    # For daily data: annual_vol = daily_vol * sqrt(252) (trading days)
    # For daily data: annual_vol = daily_vol * sqrt(365) (calendar days)
    annualized_volatility = volatility * math.sqrt(365)

    return annualized_volatility * 100  # Convert to percentage


def _calculate_max_drawdown(prices: List[float]) -> float:
    """Calculate maximum drawdown from peak."""
    if not prices:
        return 0.0

    max_drawdown = 0.0
    peak = prices[0]

    for price in prices:
        if price > peak:
            peak = price
        else:
            drawdown = (peak - price) / peak
            max_drawdown = max(max_drawdown, drawdown)

    return max_drawdown * 100  # Convert to percentage


def _calculate_sharpe_ratio(returns: List[float], risk_free_rate: float) -> float:
    """Calculate Sharpe ratio using proper annualization."""
    if not returns:
        return 0.0

    mean_return = sum(returns) / len(returns)

    # Calculate sample variance (using n-1 for sample standard deviation)
    variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
    std_dev = math.sqrt(variance)

    if std_dev == 0:
        return 0.0

    # Annualize returns and volatility (assuming daily data)
    # Daily return to annual: daily_return * 365
    # Daily volatility to annual: daily_vol * sqrt(365)
    annualized_return = mean_return * 365
    annualized_volatility = std_dev * math.sqrt(365)

    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility

    return sharpe_ratio


def _calculate_var(returns: List[float], confidence_level: float) -> float:
    """Calculate Value at Risk at given confidence level."""
    if not returns:
        return 0.0

    # Sort returns in ascending order
    sorted_returns = sorted(returns)

    # Find the percentile
    index = int((1 - confidence_level) * len(sorted_returns))
    var = sorted_returns[index]

    return var * 100  # Convert to percentage


def _calculate_apy_trend(prices: List[float], days: int) -> float:
    """Calculate APY trend over a period."""
    if len(prices) < days * 2:
        return 0.0

    # Calculate APY for the most recent period
    recent_apy = _calculate_apy(prices, days)

    # Calculate APY for the previous period
    previous_prices = prices[:-days]
    previous_apy = _calculate_apy(previous_prices, days)

    # Calculate trend (positive means increasing APY)
    trend = recent_apy - previous_apy

    return trend
