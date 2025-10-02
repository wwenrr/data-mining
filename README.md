# Data Mining - Cryptocurrency Kline Data Fetcher

A simple CLI tool to fetch cryptocurrency candlestick (kline) data from Binance API and automatically save to JSON files.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
  - [Windows](#windows)
  - [Linux](#linux)
- [Usage](#usage)
  - [Dataset Commands](#dataset-commands)
  - [Analysis Commands](#analysis-commands)
  - [Training Commands](#training-commands)
  - [Command Options](#command-options)
  - [Examples](#examples)
- [Development](#development)
  - [Code Quality](#code-quality)
- [Output](#output)
- [Project Structure](#project-structure)

## Overview

This tool provides a clean interface to fetch cryptocurrency market data from Binance API. All data is automatically saved to `data/kline/<crypto>.json` files with metadata for easy analysis.

## Features

- Fetch kline/candlestick data from Binance API
- Support all timeframes (1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
- Historical data support (fetch data from X days ago)
- Automatic data saving to JSON files
- Analyze saved kline data with comprehensive statistics
- Train machine learning models on cryptocurrency data
- Price prediction using Linear Regression or Random Forest models
- Model evaluation with detailed metrics (RMSE, MAE, R²)
- Price analysis (current, change, range)
- Volume analysis (total, average)
- Time range analysis
- Clean CLI interface with detailed logging
- Cross-platform support (Windows & Linux)

## Installation

### Windows

```powershell
# Install dependencies
.\scripts\win\install.ps1
```

### Linux

```bash
# Make scripts executable
chmod +x scripts/linux/install scripts/linux/run

# Install dependencies
./scripts/linux/install
```

## Usage

### Dataset Commands

Fetch cryptocurrency data from Binance API:

**Windows:**

```powershell
.\scripts\win\run.ps1 dataset -s <SYMBOL> -i <INTERVAL> -l <LIMIT> [-d <DAYS_AGO>]
```

**Linux:**

```bash
./scripts/linux/run dataset -s <SYMBOL> -i <INTERVAL> -l <LIMIT> [-d <DAYS_AGO>]
```

### Analysis Commands

Analyze saved cryptocurrency data:

**Windows:**

```powershell
.\scripts\win\run.ps1 analyze -c <CRYPTO>
```

**Linux:**

```bash
./scripts/linux/run analyze -c <CRYPTO>
```

### Training Commands

Train machine learning models on saved cryptocurrency data:

**Windows:**

```powershell
.\scripts\win\run.ps1 train -c <CRYPTO> -m <MODEL_TYPE> [-lb <LOOKBACK>] [-ts <TEST_SIZE>]
```

**Linux:**

```bash
./scripts/linux/run train -c <CRYPTO> -m <MODEL_TYPE> [-lb <LOOKBACK>] [-ts <TEST_SIZE>]
```

### Command Options

**Dataset Command:**

| Option       | Short | Description                             | Required | Default |
| ------------ | ----- | --------------------------------------- | -------- | ------- |
| `--symbol`   | `-s`  | Trading pair symbol (e.g., BTCUSDT)     | Yes      | -       |
| `--interval` | `-i`  | Time interval                           | Yes      | -       |
| `--limit`    | `-l`  | Number of klines to retrieve (max 1000) | No       | 100     |
| `--days`     | `-d`  | Number of days ago to start fetching    | No       | -       |

**Analyze Command:**

| Option     | Short | Description                        | Required | Default |
| ---------- | ----- | ---------------------------------- | -------- | ------- |
| `--crypto` | `-c`  | Crypto name to analyze (e.g., BTC) | Yes      | -       |

**Train Command:**

| Option        | Short | Description                                   | Required | Default |
| ------------- | ----- | --------------------------------------------- | -------- | ------- |
| `--crypto`    | `-c`  | Crypto name to train on (e.g., BTC, ETH)      | Yes      | -       |
| `--model`     | `-m`  | Model type: 'linear' or 'random_forest'       | No       | linear  |
| `--lookback`  | `-lb` | Number of periods to look back for features   | No       | 5       |
| `--test-size` | `-ts` | Proportion of data for testing (0.0-1.0)      | No       | 0.2     |

**Supported Intervals:**
`1m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1M`

### Examples

**Fetching Data:**

```powershell
# Get latest 100 daily candles for BTC/USDT
.\scripts\win\run.ps1 dataset -s BTCUSDT -i 1d -l 100

# Get 50 hourly candles for ETH/USDT
.\scripts\win\run.ps1 dataset -s ETHUSDT -i 1h -l 50

# Get 200 15-minute candles for BNB/USDT from 7 days ago
.\scripts\win\run.ps1 dataset -s BNBUSDT -i 15m -l 200 -d 7

# Get 10 daily candles for ADA/USDT from 30 days ago
.\scripts\win\run.ps1 dataset -s ADAUSDT -i 1d -l 10 -d 30
```

**Analyzing Data:**

```powershell
# Analyze BTC data
.\scripts\win\run.ps1 analyze -c BTC

# Analyze ETH data
.\scripts\win\run.ps1 analyze -c ETH

# Analyze any available crypto
.\scripts\win\run.ps1 analyze -c ADA
```

**Training Models:**

```powershell
# Train a linear regression model on BTC data
.\scripts\win\run.ps1 train -c BTC -m linear

# Train a random forest model on ETH data with custom lookback
.\scripts\win\run.ps1 train -c ETH -m random_forest -lb 10

# Train with custom test size
.\scripts\win\run.ps1 train -c BTC -m linear -lb 5 -ts 0.3
```

## Development

### Code Quality

This project uses `flake8` for linting and `black` for code formatting.

**Local Development:**

**Windows:**

```powershell
# Run linter and formatter
.\scripts\win\lint.ps1
```

**Linux:**

```bash
# Make script executable first
chmod +x scripts/linux/lint

# Run linter and formatter
./scripts/linux/lint
```

**Continuous Integration:**

The project uses GitHub Actions to automatically check code quality on Pull Requests:

- Uses Python 3.13 for compatibility with latest packages
- Runs Flake8 linting on all Python files in `src/`
- Checks Black formatting compliance
- Only triggers on PRs targeting `main`/`master` branches
- Only runs when Python files are modified
- Can also be triggered manually via GitHub Actions tab

The linter will:

1. Auto-format code with Black
2. Check code style with Flake8
3. Report any issues that need manual fixing

## Output

### Dataset Command Output

```
2025-09-30 19:34:28,779 - INFO - Retrieved 2 klines for LINKUSDT (1d)
2025-09-30 19:34:28,780 - INFO - Sample data (first 3 klines):
2025-09-30 19:34:28,780 - INFO - Kline 1:
2025-09-30 19:34:28,780 - INFO -   Open time: 1759104000000
2025-09-30 19:34:28,780 - INFO -   Open: 21.68000000
2025-09-30 19:34:28,780 - INFO -   High: 21.90000000
2025-09-30 19:34:28,780 - INFO -   Low: 20.90000000
2025-09-30 19:34:28,780 - INFO -   Close: 21.74000000
2025-09-30 19:34:28,780 - INFO -   Volume: 2497335.67000000
2025-09-30 19:34:28,780 - INFO -   Close time: 1759190399999
```

### Analysis Command Output

```
2025-09-30 19:34:22,525 - INFO - Analysis for BTCUSDT
2025-09-30 19:34:22,525 - INFO - ==================================================
2025-09-30 19:34:22,525 - INFO - Interval: 1h
2025-09-30 19:34:22,525 - INFO - Data points: 3 klines
2025-09-30 19:34:22,525 - INFO - Time range: 2025-09-30T16:00:00 -> 2025-09-30T18:59:59
2025-09-30 19:34:22,526 - INFO - Price Information:
2025-09-30 19:34:22,526 - INFO -   Current price: $113,008.00
2025-09-30 19:34:22,526 - INFO -   Price change: $226.03 (+0.20%)
2025-09-30 19:34:22,526 - INFO -   High: $113,451.89
2025-09-30 19:34:22,526 - INFO -   Low: $112,656.27
2025-09-30 19:34:22,526 - INFO - Volume Information:
2025-09-30 19:34:22,526 - INFO -   Total volume: 2,107.06
2025-09-30 19:34:22,526 - INFO -   Average volume: 702.35
2025-09-30 19:34:22,526 - INFO - Data fetched: 2025-09-30T18:46:34
```

### Train Command Output

```
2025-10-02 10:31:41,882 - INFO - Starting model training for BTC...
2025-10-02 10:31:41,882 - INFO - ==================================================
2025-10-02 10:31:41,882 - INFO - Loading data for BTC...
2025-10-02 10:31:41,883 - INFO - Loaded kline data for BTC
2025-10-02 10:31:41,883 - INFO - Preparing features with lookback=5...
2025-10-02 10:31:41,883 - INFO - Feature shape: (25, 25), Target shape: (25,)
2025-10-02 10:31:41,884 - INFO - Training linear model...
2025-10-02 10:31:41,885 - INFO - Evaluating model...
2025-10-02 10:31:41,888 - INFO - Model saved to: data/models/btc_linear_model.joblib
2025-10-02 10:31:41,888 - INFO - Scaler saved to: data/models/btc_linear_scaler.joblib
2025-10-02 10:31:41,888 - INFO - Metadata saved to: data/models/btc_linear_metadata.json
2025-10-02 10:31:41,888 - INFO -
2025-10-02 10:31:41,888 - INFO - Training completed successfully!
2025-10-02 10:31:41,888 - INFO - ==================================================
2025-10-02 10:31:41,888 - INFO - Model: linear
2025-10-02 10:31:41,888 - INFO - Crypto: BTC
2025-10-02 10:31:41,888 - INFO - Lookback: 5 periods
2025-10-02 10:31:41,888 - INFO - Feature dimensions: 25
2025-10-02 10:31:41,888 - INFO -
2025-10-02 10:31:41,888 - INFO - Training Set Metrics:
2025-10-02 10:31:41,888 - INFO -   Samples: 20
2025-10-02 10:31:41,889 - INFO -   RMSE: $0.0000
2025-10-02 10:31:41,889 - INFO -   MAE: $0.0000
2025-10-02 10:31:41,889 - INFO -   R² Score: 1.0000
2025-10-02 10:31:41,889 - INFO -
2025-10-02 10:31:41,889 - INFO - Test Set Metrics:
2025-10-02 10:31:41,889 - INFO -   Samples: 5
2025-10-02 10:31:41,889 - INFO -   RMSE: $0.0000
2025-10-02 10:31:41,889 - INFO -   MAE: $0.0000
2025-10-02 10:31:41,889 - INFO -   R² Score: 1.0000
2025-10-02 10:31:41,889 - INFO -
2025-10-02 10:31:41,889 - INFO - Model saved to: data/models/btc_linear_model.joblib
2025-10-02 10:31:41,889 - INFO - Scaler saved to: data/models/btc_linear_scaler.joblib
```

### File Output

Data is automatically saved to `data/kline/<crypto>.json`:

```json
{
  "symbol": "BTCUSDT",
  "interval": "1d",
  "limit": 5,
  "days_ago": null,
  "timestamp": "2025-09-30T18:46:34.124081",
  "klines": [
    [
      1759222800000,
      "113451.89000000",
      "113451.89000000",
      "112731.41000000",
      "112781.97000000",
      "995.05591000",
      1759226399999,
      "112534196.96416220",
      144116,
      "440.69114000",
      "49827993.67990670",
      "0"
    ]
  ]
}
```

### Kline Data Format

Each kline contains:

1. Open time (timestamp)
2. Open price
3. High price
4. Low price
5. Close price
6. Volume
7. Close time (timestamp)
8. Quote asset volume
9. Number of trades
10. Taker buy base asset volume
11. Taker buy quote asset volume
12. Ignore

## Project Structure

```
data-mining/
├── data/
│   ├── kline/              # Auto-generated JSON files for kline data
│   └── models/             # Auto-generated trained models and metadata
├── scripts/
│   ├── win/
│   │   ├── install.ps1     # Windows installation script
│   │   └── run.ps1         # Windows run script
│   └── linux/
│       ├── install         # Linux installation script
│       └── run             # Linux run script
├── src/
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── dataset.py      # Dataset command implementation
│   │   ├── analyze.py      # Analysis command implementation
│   │   └── train.py        # Training command implementation
│   ├── decorator/
│   │   └── singleton.py    # Singleton decorator
│   ├── service/
│   │   ├── binance_service.py    # Binance API service
│   │   ├── restful_service.py    # HTTP client service
│   │   ├── kline_service.py      # Kline data analysis service
│   │   └── training_service.py   # Model training service
│   └── run.py              # Main CLI entry point
├── req.txt                 # Python dependencies
└── README.md
```
