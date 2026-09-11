"""Unit tests cho CLI orchestrator (`backtest/run_backtest.py`) — Req 10.5.

Các test này kiểm tra phần điều phối/parse tham số của CLI mà KHÔNG kích hoạt
huấn luyện mô hình (vốn chậm): cấu trúc parser, hành vi khi không có cờ hành
động, chuẩn hóa cờ ``--all``, và tính chịu lỗi từng giai đoạn. Các giai đoạn nặng
được thay bằng monkeypatch để test chạy nhanh và tất định.
"""

from __future__ import annotations

import backtest.run_backtest as rb


def test_build_parser_defaults():
    """Parser có mặc định đúng cho model/cutoff/top-n và mọi cờ hành động tắt."""
    parser = rb.build_parser()
    args = parser.parse_args([])
    assert args.model_name == "LightGBM"
    assert args.cutoff == "2025Q1"
    assert args.top_n is None
    assert not (
        args.do_all
        or args.do_signals
        or args.do_walk_forward
        or args.do_interpret
        or args.do_audit
        or args.do_report
    )


def test_parser_parses_action_flags():
    """Các cờ hành động được ánh xạ đúng vào dest tương ứng."""
    parser = rb.build_parser()
    args = parser.parse_args(
        ["--interpret", "--audit", "--report", "--model", "XGBoost", "--top-n", "5"]
    )
    assert args.do_interpret and args.do_audit and args.do_report
    assert not (args.do_all or args.do_signals or args.do_walk_forward)
    assert args.model_name == "XGBoost"
    assert args.top_n == 5


def test_main_no_action_returns_2(capsys):
    """Không cờ hành động → in help và trả mã thoát 2 (lỗi sử dụng)."""
    rc = rb.main([])
    assert rc == 2
    out = capsys.readouterr().out
    assert "usage" in out.lower()


def test_all_flag_expands_to_every_stage(monkeypatch):
    """``--all`` phải gọi mọi giai đoạn đúng THỨ TỰ (Req 10.5)."""
    calls = []

    monkeypatch.setattr(
        rb, "run_signals_stage", lambda *a, **k: (calls.append("signals") or _EMPTY_SIGNALS)
    )
    monkeypatch.setattr(
        rb, "run_strategy_metrics_stage",
        lambda *a, **k: calls.append("strategy+metrics"),
    )
    monkeypatch.setattr(
        rb, "run_walk_forward", lambda *a, **k: calls.append("walk-forward")
    )
    monkeypatch.setattr(
        rb, "run_interpret_stage", lambda *a, **k: calls.append("interpret")
    )
    monkeypatch.setattr(rb, "audit_leakage", lambda *a, **k: calls.append("audit"))
    monkeypatch.setattr(
        rb, "generate_backtest_report", lambda *a, **k: calls.append("report")
    )

    failures = rb.run_backtest(do_all=True)

    assert failures == []
    assert calls == [
        "signals",
        "strategy+metrics",
        "walk-forward",
        "interpret",
        "audit",
        "report",
    ]


def test_stage_failure_is_isolated(monkeypatch):
    """Một giai đoạn lỗi được ghi nhận nhưng KHÔNG chặn các giai đoạn sau."""
    calls = []

    def _boom(*a, **k):
        raise RuntimeError("stage failed")

    monkeypatch.setattr(rb, "run_walk_forward", _boom)
    monkeypatch.setattr(
        rb, "audit_leakage", lambda *a, **k: calls.append("audit")
    )
    monkeypatch.setattr(
        rb, "generate_backtest_report", lambda *a, **k: calls.append("report")
    )

    failures = rb.run_backtest(
        do_walk_forward=True, do_audit=True, do_report=True
    )

    assert "walk-forward" in failures
    # Giai đoạn sau vẫn chạy dù walk-forward lỗi.
    assert calls == ["audit", "report"]


def test_main_returns_1_when_stage_fails(monkeypatch):
    """``main`` trả mã thoát 1 khi có ít nhất một giai đoạn thất bại."""
    monkeypatch.setattr(
        rb, "run_backtest", lambda **k: ["walk-forward"]
    )
    rc = rb.main(["--walk-forward"])
    assert rc == 1


# SignalFrame giả rỗng đủ để run_strategy_metrics_stage không được gọi thật (đã
# monkeypatch); chỉ cần khác None để nhánh chiến lược chạy.
import pandas as pd  # noqa: E402

_EMPTY_SIGNALS = pd.DataFrame(
    columns=[
        "ticker",
        "quarter_id",
        "y_true",
        "pred_label",
        "pred_proba_up",
        "period_return",
    ]
)
