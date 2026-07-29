"""Smoke tests for the experiment CLI orchestrator (``experiments/run_experiment.py``).

These tests exercise the CLI dispatch and orchestration order **without** running
real model training or reading real data. Heavy steps (snapshot, runner, reporter)
are monkeypatched so the tests stay fast and hermetic.

Covers task 7 wiring:
- ``--snapshot`` calls the snapshotter only.
- ``--experiment {id}`` follows the order snapshot → build feature → runner → report.
- ``--experiment {id}`` stops gracefully when the feature set is not available.
- ``--report`` (standalone) regenerates the text representation table.
- The soft-import feature-builder registry returns ``None`` for not-yet-implemented ids.
"""

from __future__ import annotations

import experiments.run_experiment as cli


def test_resolve_feature_builder_soft_imports_missing_module():
    """Unregistered / unknown experiment ids resolve to None (soft import).

    The soft-import contract: an id that is not in the registry (or whose builder
    module/function is unavailable) must yield ``None`` rather than raising, so the
    CLI imports cleanly regardless of which experiments are implemented.
    """
    # Unknown id (not in the registry) is None.
    assert cli.resolve_feature_builder("ZZ") is None
    # Empty string is also None.
    assert cli.resolve_feature_builder("") is None


def test_resolve_feature_builder_returns_callable_for_implemented_a3():
    """A3's builder is implemented (task 11), so it resolves to a callable."""
    assert callable(cli.resolve_feature_builder("A3"))


def test_resolve_feature_builder_returns_callable_for_implemented_a2():
    """A2's builder is implemented (task 9), so it resolves to a callable."""
    builder = cli.resolve_feature_builder("A2")
    assert callable(builder)


def test_resolve_feature_builder_returns_callable_for_implemented_a1():
    """A1a/A1b builders are implemented (task 10), so they resolve to callables."""
    assert callable(cli.resolve_feature_builder("A1a"))
    assert callable(cli.resolve_feature_builder("A1b"))


def test_snapshot_only_invokes_snapshotter(monkeypatch):
    """``--snapshot`` runs the snapshotter and nothing else."""
    calls = {"snapshot": 0, "experiment": 0}

    monkeypatch.setattr(
        cli, "create_baseline_snapshot", lambda force=False: _fake_snapshot()
    )
    monkeypatch.setattr(
        cli,
        "run_experiment",
        lambda *a, **k: calls.__setitem__("experiment", calls["experiment"] + 1),
    )

    rc = cli.main(["--snapshot"])

    assert rc == 0
    assert calls["experiment"] == 0


def test_no_action_returns_error_code():
    """No flags → prints help and returns non-zero (2)."""
    assert cli.main([]) == 2


def test_report_only_generates_text_table(monkeypatch):
    """``--report`` without ``--experiment`` regenerates the text table."""
    called = {"table": 0}

    def _fake_table(*a, **k):
        called["table"] += 1
        return "| Thuật toán | v0 |\n|---|---|\n"

    monkeypatch.setattr(cli, "generate_text_representation_table", _fake_table)
    # Avoid touching the real filesystem during the standalone-report path.
    monkeypatch.setattr(
        cli, "write_text_representation_table", lambda *a, **k: "reports/x.md"
    )

    rc = cli.main(["--report"])

    assert rc == 0
    assert called["table"] == 1


def test_report_only_persists_summary_file(monkeypatch):
    """``--report`` standalone also persists the summary via write_text_representation_table."""
    called = {"table": 0, "write": 0}

    monkeypatch.setattr(
        cli,
        "generate_text_representation_table",
        lambda *a, **k: (called.__setitem__("table", called["table"] + 1), "| t |")[1],
    )

    def _fake_write(*a, **k):
        called["write"] += 1
        return "reports/text_representation_summary.md"

    monkeypatch.setattr(cli, "write_text_representation_table", _fake_write)

    table = cli.run_report_only()

    assert table == "| t |"  # still returns the generated table string
    assert called["write"] == 1  # persistence step ran


def test_report_only_survives_persist_failure(monkeypatch):
    """A failure while persisting the summary must not crash the CLI (Req 13.8 guard)."""
    monkeypatch.setattr(
        cli, "generate_text_representation_table", lambda *a, **k: "| t |"
    )

    def _boom_write(*a, **k):
        raise OSError("disk full")

    monkeypatch.setattr(cli, "write_text_representation_table", _boom_write)

    # run_report_only must not raise despite the write failure.
    assert cli.run_report_only() == "| t |"


def test_experiment_stops_when_feature_set_unavailable(monkeypatch):
    """When builder is missing and feature file absent, runner/report never run."""
    order: list[str] = []

    monkeypatch.setattr(
        cli,
        "create_baseline_snapshot",
        lambda force=False: (order.append("snapshot"), _fake_snapshot())[1],
    )
    # No builder available.
    monkeypatch.setattr(cli, "resolve_feature_builder", lambda _id: None)
    # Feature file does not exist.
    monkeypatch.setattr(cli.Path, "exists", lambda self: False)

    def _boom_runner(cfg):  # pragma: no cover - must not be called
        order.append("runner")
        raise AssertionError("runner should not run when feature set is unavailable")

    monkeypatch.setattr(cli, "run_experiment_training", _boom_runner)

    result = cli.run_experiment("A2")

    assert result is None
    assert order == ["snapshot"]  # only the snapshot step ran


def test_experiment_full_order_with_builder(monkeypatch):
    """With a builder + report, order is snapshot → build → runner → report."""
    order: list[str] = []

    monkeypatch.setattr(
        cli,
        "create_baseline_snapshot",
        lambda force=False: (order.append("snapshot"), _fake_snapshot())[1],
    )
    monkeypatch.setattr(
        cli, "resolve_feature_builder", lambda _id: lambda: order.append("build")
    )
    # After the builder "runs", pretend the feature file exists.
    monkeypatch.setattr(cli.Path, "exists", lambda self: True)

    sentinel_result = object()

    def _fake_runner(cfg):
        order.append("runner")
        return sentinel_result

    monkeypatch.setattr(cli, "run_experiment_training", _fake_runner)

    def _fake_report(experiment_id, result, *a, **k):
        order.append("report")
        assert result is sentinel_result
        return f"reports/experiment_{experiment_id}_report.md"

    monkeypatch.setattr(cli, "generate_comparison_report", _fake_report)

    result = cli.run_experiment("A2", with_report=True)

    assert result is sentinel_result
    assert order == ["snapshot", "build", "runner", "report"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_snapshot():
    """Return a minimal object mimicking SnapshotResult for the CLI."""

    class _R:
        already_existed = True
        copied: list[str] = []
        missing: list[str] = []

    return _R()
