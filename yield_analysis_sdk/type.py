from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from .validators import (
    ChainValidatorMixin,
    UnderlyingTokenValidatorMixin,
    VaultAddressValidatorMixin,
)


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
    OTHER = "other"

    @classmethod
    def _missing_(cls, value: Any) -> "Chain":
        """Handle unknown chain values by returning OTHER."""
        return cls.OTHER


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


class RegistrationRequest(VaultAddressValidatorMixin, ChainValidatorMixin, BaseModel):
    chain: Chain
    vault_address: str


class RegistrationResponse(BaseModel):
    is_registered: bool
    message: str
    contract_tx_hash: Optional[str] = None


class Strategy(BaseModel):
    chainId: int
    address: str


class AnalysisRequest(BaseModel):
    strategies: List[Strategy]


class VaultInfo(VaultAddressValidatorMixin, ChainValidatorMixin, BaseModel):
    # Basic Vault Information
    chain: Chain
    vault_address: str
    vault_name: str
    protocol: str = Field(
        ..., description="The protocol/platform this vault belongs to"
    )

    # Fee Structure (Critical for allocation decisions)
    entry_fee_bps: int = Field(0, description="Entry fee rate in basis points")
    exit_fee_bps: int = Field(0, description="Exit fee rate in basis points")

    # Vault Capacity
    max_deposit_amount: float = Field(
        1_000_000_000_000.00,
        description="Maximum amount of underlying token that can be deposited into the vault.",
    )

    # Analysis Context
    risk_free_rate: float = Field(
        0.05, description="Risk-free rate used for Sharpe ratio calculation"
    )

    # Analysis Metadata
    last_updated_timestamp: int = Field(
        ..., description="Last update timestamp in seconds"
    )


class PerformanceAnalysis(BaseModel):
    # Core Performance Metrics (Mandatory for allocation decisions)
    apy_7d: float = Field(..., description="7-day annualized percentage yield")
    apy_30d: float = Field(..., description="30-day annualized percentage yield")
    apy_90d: float = Field(..., description="90-day annualized percentage yield")

    # Essential Risk Metrics
    volatility_30d: float = Field(..., description="30-day APY volatility")
    max_drawdown: float = Field(
        ..., description="Maximum historical drawdown percentage"
    )
    sharpe_ratio: float = Field(..., description="Risk-adjusted return ratio")

    # Current State
    current_price: float = Field(..., description="Current share price")

    # Analysis Metadata
    analysis_period_days: int = Field(
        ..., description="Number of days in the analysis period"
    )


class AnalysisResult(BaseModel):
    # Combined vault info and performance analysis
    vault_info: VaultInfo
    performance: PerformanceAnalysis
    extra_info: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional information about the vault"
    )


class AnalysisResponse(BaseModel):
    analyses: List[AnalysisResult] = Field(..., description="List of vault analyses")


class SharePriceHistory(VaultAddressValidatorMixin, BaseModel):
    vault_name: str
    vault_address: str
    price_history: List[Tuple[int, float]]
