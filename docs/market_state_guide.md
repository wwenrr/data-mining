# Hướng dẫn sử dụng Train & Market (K-Means Market States)

Tài liệu này trình bày cách huấn luyện mô hình K-Means và giải thích các feature được dùng để phân loại trạng thái thị trường (Bullish / Bearish / Sideway).

## 1. Chuẩn bị dữ liệu

1. Cài đặt dependencies (Windows):
   ```powershell
   .\scripts\win\install.ps1
   ```
2. Thu thập dữ liệu kline và lưu vào `data/kline/<crypto>.json`:
   ```powershell
   .\scripts\win\run.ps1 dataset -s BTCUSDT -i 1h -l 200 [-d <days>]
   ```
   Lặp lại khi cần cập nhật dữ liệu mới.

## 2. Huấn luyện mô hình (`train`)

```powershell
.\scripts\win\run.ps1 train -c BTC [-k <clusters>] [--min-clusters 2 --max-clusters 6]
```

- `-c / --crypto`: tên crypto trùng với file JSON (btc → `data/kline/btc.json`).
- `-k / --clusters`: nếu bỏ trống, công cụ dùng Silhouette để tự chọn K trong khoảng `min`→`max`.
- `--min-clusters`, `--max-clusters`: giới hạn range khi auto-select K.

Kết quả tạo file mô hình tại `models/<symbol>_<interval>.joblib` (ví dụ `models/btcusdt_1h.joblib`) và log mean future return của từng cụm:

```
Cluster 5 → Bullish (mean future return: 0.0003)
Cluster 2 → Bearish (mean future return: -0.0026)
...
```

> Nên train lại sau khi kéo dữ liệu mới hoặc muốn thay đổi số cụm.

## 3. Phân loại trạng thái (`market`)

```powershell
.\scripts\win\run.ps1 market -c BTC [--show-history]
```

- Gọi mô hình đã train để xác định trạng thái của candle mới nhất.
- Hiển thị: timestamp, giá, cluster, nhãn Bull/Bear/Sideway và snapshot các feature tại thời điểm đó.
- `--show-history` in thêm JSON phân bố số lượng trạng thái lịch sử.

Ví dụ:

```
Latest timestamp: 2025-11-16T08:00:00
Closing price: $96,116.94
Cluster 0 → Sideway
Feature snapshot:
  return: 0.000176
  volatility_7: 0.002969
  ...
State distribution:
  Sideway: 108
  Bullish: 27
  Bearish: 15
```

## 4. Ý nghĩa các feature

| Feature          | Mô tả                                                                 | Gợi ý diễn giải                                                                 |
| ---------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `return`         | % thay đổi giá của candle hiện tại so với candle trước                | >0 là tăng, <0 là giảm; giá trị lớn → biến động mạnh                             |
| `volatility_7`   | Độ lệch chuẩn của `return` trong 7 phiên gần nhất                     | Đo biến động ngắn hạn; cao → thị trường nhiễu                                   |
| `volatility_14`  | Độ lệch chuẩn của `return` trong 14 phiên                             | Tương tự nhưng dài hơn, để so sánh short-term vs mid-term                        |
| `ma_7`           | Trung bình động 7 kỳ của giá đóng cửa                                 | Thể hiện xu hướng rất ngắn hạn                                                  |
| `ma_14`          | Trung bình động 14 kỳ                                                 | Dài hơn, dùng để so với MA7                                                     |
| `ma_50`          | Trung bình động 50 kỳ                                                 | Xu hướng trung hạn                                                              |
| `ma_slope`       | `ma_7 - ma_14`                                                        | >0 → xu hướng ngắn hạn mạnh hơn trung hạn (Bullish), <0 → ngược lại             |
| `rsi_14`         | Relative Strength Index 14 kỳ                                         | >70 quá mua, <30 quá bán; 50 là trung tính                                      |
| `macd`           | EMA12 - EMA26                                                         | >0 báo hiệu uptrend, <0 downtrend                                               |
| `macd_signal`    | EMA9 của MACD                                                         | MACD cắt lên signal → bullish momentum, cắt xuống → bearish                     |
| `volume_change`  | % thay đổi khối lượng so với phiên trước                              | Khối lượng tăng kèm giá tăng → xác nhận xu hướng                                |
| `future_return_1`| (Chỉ dùng khi train) lợi nhuận dự kiến ở candle tiếp theo             | Dùng để gán nhãn Bull/Bear/Sideway (Mean future return cao → Bullish)           |

## 5. Best practices

1. Luôn đảm bảo dữ liệu có đủ chiều dài để tính feature (ít nhất 50 candle cho MA50).
2. Nếu model auto-chọn K quá cao / nhiễu, fix `-k 3` để giữ đúng 3 trạng thái.
3. Khi cluster Bullish có mean future return cao và bền, trạng thái market “tốt”. Nếu các cụm không khác biệt nhiều, cân nhắc thêm feature mới (ATR, volume imbalance, v.v.).
4. Sau khi cập nhật dữ liệu bằng `dataset`, nên chạy lại `train` trước khi `market` để đảm bảo state mới phản ánh mô hình gần nhất.
