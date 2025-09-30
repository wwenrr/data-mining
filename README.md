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
│   └── kline/              # Auto-generated JSON files
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
│   │   └── analyze.py      # Analysis command implementation
│   ├── decorator/
│   │   └── singleton.py    # Singleton decorator
│   ├── service/
│   │   ├── binance_service.py    # Binance API service
│   │   ├── restful_service.py    # HTTP client service
│   │   └── kline_service.py      # Kline data analysis service
│   └── run.py              # Main CLI entry point
├── req.txt                 # Python dependencies
└── README.md
```
