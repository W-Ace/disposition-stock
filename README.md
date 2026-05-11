# 處置股看板 (disposition-stock)

台股「風險股 / 處置中 / 即將出關」每日觀察站。資料來源：TWSE / TPEx 公告 + FinLab 補價量。

## 結構

```
notes/        研究筆記（規則、策略構想、永豐串接）
scraper/      Python 抓資料 + 分類 → snapshot.json
web/          Vite + Vue3 SPA，部署 GitHub Pages
.github/      Actions：21:35 排程更新 + push 觸發部署
```

## 開發

### 後端

```bash
conda activate trade
pip install -e ./scraper
python -m scraper.main --output web/public/data/snapshot.json
# --date YYYY-MM-DD 指定交易日
```

需要環境變數 `FINLAB_API_TOKEN`。**19:00 前跑會抓到前一交易日資料**（FinLab 更新時點），所以本地測試請晚上 7 點後跑。

### 前端

```bash
cd web
npm install
npm run dev
```

### 排程

GitHub Actions 每個交易日 **21:35 台北**自動跑（避開 FinLab 19:00 / 融資融券 21:30 更新前的 stale 資料）。需要在 repo 設 Secret `FINLAB_API_TOKEN`。

## 分類規則

| 桶 | 判定 |
|---|---|
| 風險股 | 未處置 ∧ 30 日累計注意 ≥ 4 次 |
| 處置中 | 今日 ∈ [處置起日, 處置迄日] |
| 即將出關 | 處置迄日 − 今日 ≤ 1 個營業日 |

處置股規則詳見 [`notes/02-rules-disposition.md`](notes/02-rules-disposition.md)。

## 資料源

全部走 FinLab：

| 表 | 用途 |
|---|---|
| `disposal_information` | 處置事件（含 5/20 分盤、起迄日、措施）— TWSE + TPEx |
| `trading_attention` | 注意事件 log，數 30 日累計次數用 |
| `company_basic_info` | 公司簡稱、產業類別、市場別 |
| `price:收盤價` / `price:成交金額` | 行情 |
| `intraday_trading:*` | 當沖標記 |

直爬 TWSE/TPEx 已棄用（IP rate limit 嚴格，且資料 FinLab 都有）。詳見 [`notes/03-data-sources.md`](notes/03-data-sources.md)。
