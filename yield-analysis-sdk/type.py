from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List, Dict

class Chain(Enum):
    ETHEREUM = "ethereum"
    ARBITRUM = "arbitrum"
    BASE = "base"
    OPTIMISM = "optimism"
    POLYGON = "polygon"
    BSC = "bsc"
    GNOS = "gnos"
    AVALANCHE = "avalanche"
    FANTOM = "fantom"
    HARMONY = "harmony"
    MOONBEAM = "moonbeam"
    MOONRIVER = "moonriver"

class StrategyType(Enum):
    # Core Yield Strategies
    LIQUID_STAKING = "liquid_staking"
    LIQUID_RESTAKING = "liquid_restaking"
    LENDING = "lending"
    YIELD_AGGREGATOR = "yield_aggregator"
    
    # Trading & DeFi
    BASIS_TRADING = "basis_trading"
    ARBITRAGE = "arbitrage"
    CDP = "cdp"
    DEXES = "dexes"
    
    # Index & Basket
    INDEXES = "index"
    BASKET = "basket"
    
    # Farming
    YIELD_FARMING = "yield_farming"
    LIQUIDITY_MINING = "liquidity_mining"
    
    # Other
    OTHER = "other"

class AuditStatus(Enum):
    AUDITED = "audited"
    NOT_AUDITED = "not_audited"
    PARTIALLY_AUDITED = "partially_audited"
    UNKNOWN = "unknown"

class AnalysisRequest(BaseModel):
    lookback_window_in_days: int = Field(..., description="The lookback window in days")


class VaultInfo(BaseModel):
    # Basic Vault Information
    chain: Chain
    vault_address: str
    vault_name: str
    
    # Fee Structure (Critical for allocation decisions)
    entry_fee_percentage: float = Field(0.0, description="Entry fee as percentage")
    exit_fee_percentage: float = Field(0.0, description="Exit fee as percentage")
    
    # Analysis Context
    risk_free_rate: float = Field(0.05, description="Risk-free rate used for Sharpe ratio calculation")
    
    # Analysis Metadata
    last_updated_timestamp: int = Field(..., description="Last update timestamp in seconds")
    data_source: Optional[str] = Field(None, description="Source of the data")

class PerformanceAnalysis(BaseModel):
    # Core Performance Metrics (Mandatory for allocation decisions)
    apy_7d: float = Field(..., description="7-day annualized percentage yield")
    apy_30d: float = Field(..., description="30-day annualized percentage yield")
    apy_90d: float = Field(..., description="90-day annualized percentage yield")
    
    # Essential Risk Metrics
    volatility_30d: float = Field(..., description="30-day APY volatility")
    max_drawdown: float = Field(..., description="Maximum historical drawdown percentage")
    sharpe_ratio: float = Field(..., description="Risk-adjusted return ratio")
    
    # Current State
    current_price: float = Field(..., description="Current share price")
    
    # Analysis Metadata
    analysis_period_days: int = Field(..., description="Number of days in the analysis period")

class VaultPerformanceAnalysis(BaseModel):
    # Combined vault info and performance analysis
    vault_info: VaultInfo
    performance: PerformanceAnalysis

class AnalysisResponse(BaseModel):
    analyses: list[VaultPerformanceAnalysis] = Field(..., description="List of vault analyses")
    total_count: int = Field(..., description="Total number of analyses")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")


