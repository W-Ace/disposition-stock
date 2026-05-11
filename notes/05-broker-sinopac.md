# 永豐 API 串接備忘

本期**不在這個專案串自動下單**。已有其他自動化流程處理永豐 Shioaji API。本檔只記錄未來若要從 FinLab 直接下單的整合方式。

## FinLab + 永豐

```python
from finlab.online.sinopac_account import SinopacAccount
from finlab.online.order_executor import OrderExecutor, Position

acc = SinopacAccount()  # 自動讀 SHIOAJI_API_KEY / SHIOAJI_SECRET_KEY 環境變數
position = Position.from_report(report, fund=1_000_000)
executor = OrderExecutor(position, account=acc)
executor.create_orders(view_only=True)  # 先預覽
executor.create_orders()                # 實際下單
```

## 環境變數

需要在 shell / .env 設好：
- `SHIOAJI_API_KEY`
- `SHIOAJI_SECRET_KEY`
- `SHIOAJI_CERT_PERSON_ID`
- `SHIOAJI_CERT_PASSWORD`
- `SHIOAJI_CA_PATH`

## 注意事項

- 處置股下單要先**圈存款券**（永豐 Shioaji 有對應參數）
- 5 分盤 / 20 分盤是**集合競價**，市價單行為與一般盤不同
- 第二次處置需「全面預收款券」，下單前必須先入金

## 替代路線

如 FinLab 整合有限制（例如部分商品不支援），改為：
1. FinLab 只當資料源 → 自己呼叫 Shioaji
2. 用既有自動化流程接收訊號後下單
