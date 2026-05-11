"""FinLab-based enrichment: name, industry, market, price, value, intraday flag.

Loads each FinLab table once and looks up per-stock fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class Enrichment:
    name: str | None
    industry: str | None
    market: str | None                # 'TWSE' or 'TPEx'
    close: float | None
    change: float | None
    change_pct: float | None
    value_100m: float | None          # 成交值（億）
    can_intraday: bool


_MARKET_MAP = {"sii": "TWSE", "otc": "TPEx", "rotc": "Emerging"}


def enrich(codes: Iterable[str]) -> dict[str, Enrichment]:
    """Per-stock enrichment from FinLab. Falls back to None fields on error."""
    code_set = set(codes)
    out: dict[str, Enrichment] = {
        c: Enrichment(None, None, None, None, None, None, None, False)
        for c in code_set
    }
    if not code_set:
        return out

    from finlab import data

    info = data.get("company_basic_info")
    info_map = {str(r["symbol"]): r for _, r in info.iterrows() if str(r["symbol"]) in code_set}

    close_df = data.get("price:收盤價")
    value_series = data.get("price:成交金額").iloc[-1] / 1e8
    close = close_df.iloc[-1]
    prev_close = close_df.iloc[-2]

    try:
        intraday_map = data.get("intraday_trading:得先賣後買當沖").iloc[-1].to_dict()
    except Exception:
        intraday_map = {}

    for code in code_set:
        meta = info_map.get(code)
        c = float(close[code]) if code in close.index and close[code] == close[code] else None
        pc = float(prev_close[code]) if code in prev_close.index and prev_close[code] == prev_close[code] else None
        chg = (c - pc) if (c is not None and pc is not None) else None
        chg_pct = (chg / pc * 100) if (chg is not None and pc) else None
        v = float(value_series[code]) if code in value_series.index and value_series[code] == value_series[code] else None
        out[code] = Enrichment(
            name=str(meta["公司簡稱"]).strip() if meta is not None else None,
            industry=str(meta["產業類別"]).strip() if meta is not None else None,
            market=_MARKET_MAP.get(str(meta["市場別"]).strip()) if meta is not None else None,
            close=c, change=chg, change_pct=chg_pct, value_100m=v,
            can_intraday=bool(intraday_map.get(code, False)),
        )
    return out
