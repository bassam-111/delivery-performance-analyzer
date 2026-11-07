"""Delivery Performance Analyzer.

Reads a CSV of operational deliveries (task, client, owner, due date,
completed date, status) and prints an on-time performance summary, plus
per-client and per-owner breakdowns saved as CSV files.

Usage:
    python analyzer.py
    python analyzer.py --input data/deliveries.csv --output-dir output
    python analyzer.py --as-of 2026-10-20

Only completed tasks count toward the on-time rate. Open tasks past
their due date are flagged as overdue; open tasks due within 2 days
of --as-of are flagged as at risk.
"""

import argparse
from pathlib import Path

import pandas as pd

DEFAULT_INPUT = Path(__file__).parent / "data" / "deliveries.csv"
DEFAULT_OUTPUT = Path(__file__).parent / "output"


def load_deliveries(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["due_date", "completed_date"])
    required = {"task_id", "client", "owner", "task", "due_date", "status"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return df


def summarize(df: pd.DataFrame, as_of: pd.Timestamp) -> dict:
    completed = df[df["status"] == "completed"].copy()
    completed["delay_days"] = (
        completed["completed_date"] - completed["due_date"]
    ).dt.days
    completed["on_time"] = completed["delay_days"] <= 0

    open_tasks = df[df["status"] != "completed"].copy()
    open_tasks["days_to_due"] = (open_tasks["due_date"] - as_of).dt.days
    overdue = open_tasks[open_tasks["days_to_due"] < 0]
    at_risk = open_tasks[(open_tasks["days_to_due"] >= 0)
                         & (open_tasks["days_to_due"] <= 2)]

    late = completed[~completed["on_time"]]
    return {
        "total": len(df),
        "completed": len(completed),
        "open": len(open_tasks),
        "on_time_rate": round(completed["on_time"].mean() * 100, 1)
        if len(completed) else 0.0,
        "avg_late_days": round(late["delay_days"].mean(), 1)
        if len(late) else 0.0,
        "overdue_open": len(overdue),
        "at_risk_open": len(at_risk),
        "overdue_tasks": overdue,
        "at_risk_tasks": at_risk,
        "completed_df": completed,
    }


def breakdown(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    completed = df[df["status"] == "completed"].copy()
    completed["delay_days"] = (
        completed["completed_date"] - completed["due_date"]
    ).dt.days
    completed["on_time"] = completed["delay_days"] <= 0
    grouped = completed.groupby(group_col).agg(
        completed_tasks=("task_id", "count"),
        on_time_tasks=("on_time", "sum"),
        avg_delay_days=("delay_days", "mean"),
    ).reset_index()
    grouped["on_time_pct"] = (
        grouped["on_time_tasks"] / grouped["completed_tasks"] * 100
    ).round(1)
    grouped["avg_delay_days"] = grouped["avg_delay_days"].round(1)
    return grouped.sort_values("on_time_pct")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--as-of", default="2026-10-20",
                        help="Reference date for overdue/at-risk flags.")
    args = parser.parse_args()

    df = load_deliveries(args.input)
    as_of = pd.Timestamp(args.as_of)
    summary = summarize(df, as_of)

    print(f"Deliveries analyzed: {summary['total']}")
    print(f"Completed: {summary['completed']} | Open: {summary['open']}")
    print(f"On-time rate (completed tasks): {summary['on_time_rate']}%")
    print(f"Average delay on late tasks: {summary['avg_late_days']} days")
    print(f"Overdue open tasks: {summary['overdue_open']}")
    print(f"At-risk open tasks (due within 2 days): "
          f"{summary['at_risk_open']}")
    print()
    if len(summary["overdue_tasks"]):
        print("Overdue:")
        for _, row in summary["overdue_tasks"].iterrows():
            print(f"  - #{row['task_id']} {row['task']} "
                  f"({row['client']}, due {row['due_date'].date()})")
    if len(summary["at_risk_tasks"]):
        print("At risk:")
        for _, row in summary["at_risk_tasks"].iterrows():
            print(f"  - #{row['task_id']} {row['task']} "
                  f"({row['client']}, due {row['due_date'].date()})")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    by_client = breakdown(df, "client")
    by_owner = breakdown(df, "owner")
    by_client.to_csv(args.output_dir / "client_summary.csv", index=False)
    by_owner.to_csv(args.output_dir / "owner_summary.csv", index=False)
    print()
    print("Per-client summary:")
    print(by_client.to_string(index=False))
    print()
    print("Per-owner summary:")
    print(by_owner.to_string(index=False))
    print()
    print(f"Reports written to {args.output_dir}/")


if __name__ == "__main__":
    main()
