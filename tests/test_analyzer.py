import pandas as pd

from analyzer import breakdown, load_deliveries, summarize


def test_analyzer_summarizes_sample_deliveries_csv(tmp_path):
    csv_path = tmp_path / "deliveries.csv"
    csv_path.write_text(
        "task_id,client,owner,task,due_date,completed_date,status\n"
        "1,Acme,Ada,Prepare report,2026-10-19,2026-10-19,completed\n"
        "2,Acme,Bob,Review report,2026-10-18,2026-10-20,completed\n"
        "3,Globex,Ada,Send invoice,2026-10-20,,open\n"
        "4,Globex,Bob,Archive files,2026-10-15,,open\n",
        encoding="utf-8",
    )

    deliveries = load_deliveries(csv_path)
    summary = summarize(deliveries, pd.Timestamp("2026-10-20"))
    client_summary = breakdown(deliveries, "client")

    assert summary["total"] == 4
    assert summary["completed"] == 2
    assert summary["open"] == 2
    assert summary["on_time_rate"] == 50.0
    assert summary["avg_late_days"] == 2.0
    assert summary["overdue_open"] == 1
    assert summary["at_risk_open"] == 1
    assert set(summary["overdue_tasks"]["task_id"]) == {4}
    assert set(summary["at_risk_tasks"]["task_id"]) == {3}
    assert client_summary.set_index("client").loc["Acme", "on_time_pct"] == 50.0
