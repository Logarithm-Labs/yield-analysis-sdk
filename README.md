# Yield Analysis SDK

A Python SDK for DeFi vault registration and yield analysis services within the Agent Commerce Protocol (ACP) ecosystem.

## 🚀 Features

- **ACP Integration**: Built-in support for Virtuals ACP (Agent Commerce Protocol)
- **Vault Registration**: Complete workflow for registering DeFi vaults in the ACP ecosystem
- **Yield Analysis Service**: AI-powered vault performance analysis and metrics calculation
- **Multi-chain Support**: Ethereum, Arbitrum, Base, Optimism, Polygon, BSC, and more
- **Comprehensive Metrics**: APY calculations, volatility analysis, Sharpe ratios, and drawdown tracking
- **Real-time Data**: Fetch vault performance from blockchain subgraphs
- **Type Safety**: Full Pydantic validation and type hints

## 📦 Installation

```bash
pip install git+ssh://git@github.com/Logarithm-Labs/yield-analysis-sdk.git#egg=yield_analysis_sdk
```

## 🔧 Quick Start

For detailed usage examples, see the `examples/` directory:

- **`examples/analysis_service.py`**: Analysis service implementation
- **`examples/registration.py`**: Vault registration and job management

### Basic Usage

```python
from yield_analysis_sdk import Chain, analyze_yield_with_daily_share_price

# See examples/analysis_service.py for complete implementation
```

## 🏗️ ACP Ecosystem Integration

This SDK provides two main services within the ACP ecosystem:

### Vault Registration Service
- Register new DeFi vaults for analysis
- Validate vault addresses and chain compatibility
- Manage registration workflow through ACP jobs

### Yield Analysis Service
- Provide vault performance analysis as an ACP service
- Calculate comprehensive yield metrics
- Deliver analysis results through ACP job completion

## 📊 Supported Metrics

- **APY Calculations**: 7-day, 30-day, 90-day annualized yields
- **Risk Metrics**: Volatility, maximum drawdown, Sharpe ratio
- **Vault Info**: Fees, capacity limits, audit status
- **Multi-chain**: Cross-chain vault comparison


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- **Email**: dev@logarithm.fi
- **Issues**: [GitHub Issues](https://github.com/yourusername/yield-analysis-sdk/issues)
