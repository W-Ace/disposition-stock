# 資料來源

**結論：全部用 FinLab，不直爬 TWSE/TPEx。**

FinLab 內建表已涵蓋上市+上櫃、含 5/20 分盤、含第一次/第二次處置、歷史回溯到 2008。最初以為 `data.search('處置')` 為空就放棄是搜得不夠廣 — 正確的關鍵字是 `disposal` / `attention`。

## 主要表

| 表名 | 內容 | 欄位 |
|---|---|---|
| `disposal_information` | 處置事件 log（7,000+ 列） | symbol, date, 證券名稱, 處置條件, 處置措施, 處置內容, **處置開始時間**, **處置結束時間**, **分時交易**(5/20/25/...), stock_id |
| `trading_attention` | 注意事件 log（86,000+ 列） | symbol, date, **注意交易資訊**(含第X款), 收盤價, 本益比, stock_id |
| `etl:disposal_stock_filter` | 處置股每日 boolean 矩陣（2,739 檔 × 9,000+ 日） | DataFrame[date × stock]: True/False |
| `change_transaction:變更交易` | 變更交易方法（全額交割、停止交易等） | DataFrame[date × stock] |

## 補充表（enrich）

| 表 | 用途 |
|---|---|
| `company_basic_info` | 公司簡稱、產業類別、市場別（sii=上市、otc=上櫃） |
| `price:收盤價` / `price:成交金額` | 即時行情、漲跌計算 |
| `intraday_trading:得先賣後買當沖` | 資/券/沖 旗標 |
| `security_lending_sell:借券賣出` | 借券動能（策略用） |
| `security_industry_themes` | 主題股分類（半導體、AI、CCL...） |

## 處置措施 enum（取自實際資料）

| 措施 | 出現次數 | 5/20 分盤 |
|---|---|---|
| 第一次處置 | 3,643 | 通常 5 |
| 第二次處置 | 2,118 | 通常 20 |
| 收足五成款券 | 645 | NaN |
| 收足全部款券 | 638 | NaN |
| 人工管制撮合 | 283 | 30/45/60 |
| 督導會報決議 | 80 | NaN |
| 其他處置 | 19 | — |

## 更新時間

FinLab 一般資料 **19:00 後**更新當日；融資融券資料 **21:30 後**。所以排程必須在 19:00 後（含融資融券就 21:30 後）。本專案排 **21:35 台北**。

## 直爬 TWSE/TPEx 的歷史記錄（已不用）

| 用途 | URL |
|---|---|
| TWSE 處置 | `https://www.twse.com.tw/rwd/zh/announcement/punish?response=json&date=YYYYMMDD` |
| TWSE 注意 | `https://www.twse.com.tw/rwd/zh/announcement/notice?response=json&date=YYYYMMDD` |
| TPEx 處置 | `https://www.tpex.org.tw/openapi/v1/tpex_disposal_information` |

TWSE 端點對單一 IP rate limit 嚴格（封 30+ 分鐘）。FinLab 把這部份統一處理掉了，是改用 FinLab 的主要動機之一。
