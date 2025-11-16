# Market State Training & Forecast Guide

This guide explains how to use the CLI workflow to train the K-Means clustering model, classify the latest market state, train a supervised classifier, and forecast the next state. All commands assume you already created a dataset JSON file via the `dataset` command.

## 1. Prepare the data

1. Install dependencies (Windows example):
   ```powershell
   .\scripts\win\install.ps1
   ```
2. Fetch klines and save to `data/kline/<crypto>.json`:
   ```powershell
   .\scripts\win\run.ps1 dataset -s BTCUSDT -i 1h -l 200 [-d <days>]
   ```
   Repeat whenever you need fresher data.

## 2. Train the clustering model (`train`)

```powershell
.\scripts\win\run.ps1 train -c BTC [-k <clusters>] [--min-clusters 2 --max-clusters 6]
```

- `-c / --crypto`: matches the JSON filename (e.g., `btc` -> `data/kline/btc.json`).
- `-k / --clusters`: fix the number of clusters; otherwise the tool auto-selects K using the silhouette score in the provided range.
- `--min-clusters`, `--max-clusters`: bounds for auto-selection.

Output includes the path to `models/<symbol>_<interval>.joblib` and the mean future return per cluster, which is used to label clusters as Bullish/Bearish/Sideway.

## 3. Classify the latest state (`market`)

```powershell
.\scripts\win\run.ps1 market -c BTC [--show-history]
```

- Loads the trained K-Means model, labels every candle, and prints the latest timestamp, price, cluster, and label.
- `--show-history` prints a JSON distribution of Bullish/Bearish/Sideway counts.

Example snippet:

```
Latest timestamp: 2025-11-16T08:00:00
Closing price: $96,116.94
Cluster 0 -> Sideway
State distribution:
  Sideway: 108
  Bullish: 27
  Bearish: 15
```

## 4. Train the supervised classifier (`train-classifier`)

After clustering, train a RandomForest classifier to predict the **next** state based on current features:

```powershell
.\scripts\win\run.ps1 train-classifier -c BTC [--test-size 0.25] [--estimators 300]
```

- Input data: feature frame with Bull/Bear/Sideway labels from the K-Means model.
- Target: `next_state = state.shift(-1)` (the label of the following candle).
- Output: train/test accuracy, classification report, confusion matrix, and `models/<symbol>_<interval>_classifier.joblib`.

## 5. Forecast the next state (`forecast`)

```powershell
.\scripts\win\run.ps1 forecast -c BTC
```

- Loads the classifier, scales the latest feature vector, and predicts the next state's label with probabilities.
- Use together with `market` to track both the current label (unsupervised) and the expected next label (supervised).

## 6. Feature reference

| Feature          | Description                                                                 | Interpretation tip                                                                |
| ---------------- | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `return`         | Percent change of close price vs. previous candle                           | Positive = gain, negative = loss                                                  |
| `volatility_7`   | Rolling std-dev of `return` over 7 candles                                  | Short-term volatility                                                             |
| `volatility_14`  | Rolling std-dev of `return` over 14 candles                                 | Medium-term volatility                                                            |
| `ma_7`           | 7-period moving average of close                                            | Very short-term trend                                                             |
| `ma_14`          | 14-period moving average                                                    | Short-term trend                                                                  |
| `ma_50`          | 50-period moving average                                                    | Mid-term trend                                                                    |
| `ma_slope`       | `ma_7 - ma_14`                                                              | Positive when fast MA above slow MA (bullish momentum)                            |
| `rsi_14`         | Relative Strength Index                                                     | >70 overbought, <30 oversold, ~50 neutral                                         |
| `macd`           | EMA12 - EMA26                                                               | Positive implies upward momentum                                                  |
| `macd_signal`    | EMA9 of MACD                                                                | MACD crossing above signal is bullish, below is bearish                           |
| `volume_change`  | Percent change of volume vs. previous candle                                | Rising volume supports the move                                                   |
| `future_return_1`| (training only) future return over the next candle                          | Used to compute mean return per cluster                                           |

## 7. Best practices

1. Ensure at least 50 candles so MA50 and other rolling windows are valid.
2. If automatic K selection yields noisy clusters, fix `-k 3` to force Bull/Bear/Sideway.
3. Cluster quality is 'good' when Bullish mean future return is clearly positive and Bearish clearly negative; otherwise enrich the feature set.
4. After updating data with `dataset`, re-run `train` (K-Means) and `train-classifier` before calling `market`/`forecast` so both models reflect the latest history.
