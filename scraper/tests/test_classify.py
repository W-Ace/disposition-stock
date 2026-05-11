from datetime import date

from scraper.classify import classify
from scraper.source import DisposalRow, _is_common_stock, coalesce_per_stock


def _row(code: str, start: date, end: date, measure="第一次處置", minutes=5) -> DisposalRow:
    return DisposalRow(
        code=code, name=f"N{code}", measure=measure, auction_minutes=minutes,
        period_start=start, period_end=end, condition="x", prepay_full=False,
    )


def test_disposal_vs_exiting():
    today = date(2026, 5, 12)  # Tuesday
    rows = [
        _row("1001", date(2026, 5, 12), date(2026, 5, 25)),  # 9 weekdays left -> disposal
        _row("1002", date(2026, 4, 28), date(2026, 5, 13)),  # 1 weekday left -> exiting
        _row("1003", date(2026, 4, 28), date(2026, 5, 12)),  # last day -> exiting
    ]
    out = classify(today, rows, {})
    by_code = {s.code: s.bucket for s in out}
    assert by_code["1001"] == "disposal"
    assert by_code["1002"] == "exiting"
    assert by_code["1003"] == "exiting"


def test_risk_threshold():
    from scraper.classify import RISK_THRESHOLD
    today = date(2026, 5, 12)
    counts = {
        "1001": RISK_THRESHOLD + 2,
        "1002": RISK_THRESHOLD - 1,
        "1003": RISK_THRESHOLD,
    }
    out = classify(today, [], counts)
    risk_codes = {s.code for s in out if s.bucket == "risk"}
    assert risk_codes == {"1001", "1003"}


def test_in_disposal_skips_risk():
    today = date(2026, 5, 12)
    rows = [_row("1001", date(2026, 5, 12), date(2026, 5, 25))]
    out = classify(today, rows, {"1001": 10})
    assert [s.bucket for s in out if s.code == "1001"] == ["disposal"]


def test_outside_period_not_classified():
    """Active-disposal filtering happens upstream in load_active_disposals;
    classify() trusts its input as currently-active."""
    today = date(2026, 5, 12)
    out = classify(today, [], {})
    assert out == []


def test_common_stock_filter():
    assert _is_common_stock("2330")
    assert _is_common_stock("2330L")
    assert not _is_common_stock("0050")     # ETF
    assert not _is_common_stock("00646")    # ETF
    assert not _is_common_stock("30165")    # CB
    assert not _is_common_stock("731240")   # warrant


def test_coalesce_prefers_second_disposition():
    today = date(2026, 5, 12)
    a = _row("1001", date(2026, 5, 7), date(2026, 5, 20), "第一次處置", 5)
    b = _row("1001", date(2026, 5, 12), date(2026, 5, 25), "第二次處置", 20)
    out = coalesce_per_stock([a, b])
    assert len(out) == 1 and out[0].measure == "第二次處置"
