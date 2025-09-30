# Data Mining - Cryptocurrency Kline Data Fetcher

A simple CLI tool to fetch cryptocurrency candlestick (kline) data from Binance API and automatically save to JSON files.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
  - [Windows](#windows)
  - [Linux](#linux)
- [Usage](#usage)
  - [Basic Commands](#basic-commands)
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

### Basic Commands

**Windows:**

```powershell
.\scripts\win\run.ps1 -s <SYMBOL> -i <INTERVAL> -l <LIMIT> [-d <DAYS_AGO>]
```

**Linux:**

```bash
./scripts/linux/run -s <SYMBOL> -i <INTERVAL> -l <LIMIT> [-d <DAYS_AGO>]
```

### Command Options

| Option       | Short | Description                             | Required | Default |
| ------------ | ----- | --------------------------------------- | -------- | ------- |
| `--symbol`   | `-s`  | Trading pair symbol (e.g., BTCUSDT)     | Yes      | -       |
| `--interval` | `-i`  | Time interval                           | Yes      | -       |
| `--limit`    | `-l`  | Number of klines to retrieve (max 1000) | No       | 100     |
| `--days`     | `-d`  | Number of days ago to start fetching    | No       | -       |

**Supported Intervals:**
`1m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1M`

### Examples

```powershell
# Get latest 100 daily candles for BTC/USDT
.\scripts\win\run.ps1 -s BTCUSDT -i 1d -l 100

# Get 50 hourly candles for ETH/USDT
.\scripts\win\run.ps1 -s ETHUSDT -i 1h -l 50

# Get 200 15-minute candles for BNB/USDT from 7 days ago
.\scripts\win\run.ps1 -s BNBUSDT -i 15m -l 200 -d 7

# Get 10 daily candles for ADA/USDT from 30 days ago
.\scripts\win\run.ps1 -s ADAUSDT -i 1d -l 10 -d 30
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

- Runs Flake8 linting on all Python files in `src/`
- Checks Black formatting compliance
- Only triggers on PRs targeting `main`/`master` branches
- Only runs when Python files are modified

The linter will:

1. Auto-format code with Black
2. Check code style with Flake8
3. Report any issues that need manual fixing

## Output

### Console Output

```
Retrieved 5 klines for BTCUSDT (1d)
Sample data (first 3 klines):
Kline 1:
  Open time: 1759222800000
  Open: 113451.89000000
  High: 113451.89000000
  Low: 112731.41000000
  Close: 112781.97000000
  Volume: 995.05591000
  Close time: 1759226399999
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
│   │   └── dataset.py      # Dataset command implementation
│   ├── decorator/
│   │   └── singleton.py    # Singleton decorator
│   ├── service/
│   │   ├── binance_service.py    # Binance API service
│   │   └── restful_service.py    # HTTP client service
│   └── run.py              # Main CLI entry point
├── req.txt                 # Python dependencies
└── README.md
```
