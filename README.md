# Delivery Performance Analyzer

A small Python/Pandas command-line tool for operations work: it reads a
CSV of deliveries (task, client, owner, due date, completed date,
status) and reports on-time performance, late-task delays, and
overdue/at-risk open work, with per-client and per-owner breakdowns.

Built with skills from the resume only: Python and Pandas, plus CSV
reporting. No external services, no claimed expertise beyond that.

## What it does

- On-time rate across completed tasks, and average delay on late tasks
- Flags open tasks that are overdue or due within 2 days of a
  reference date (`--as-of`)
- Per-client and per-owner summaries, saved as CSV files for
  follow-up or a weekly ops review

## Files

- `analyzer.py` — the analyzer (CLI, Pandas)
- `data/deliveries.csv` — sample dataset: 20 deliveries across
  3 clients and 3 owners (illustrative data, not real client data)
- `requirements.txt` — Pandas
- `output/` — generated reports (`client_summary.csv`,
  `owner_summary.csv`)

## How to run

```bash
pip install -r requirements.txt
python analyzer.py
# Or with your own file and reference date:
python analyzer.py --input data/deliveries.csv --as-of 2026-10-20
```

## Sample output

Using the bundled sample data (reference date 2026-10-20):

```
Deliveries analyzed: 20
Completed: 17 | Open: 3
On-time rate (completed tasks): 70.6%
Average delay on late tasks: 2.4 days
Overdue open tasks: 3
At-risk open tasks (due within 2 days): 0

Overdue:
  - #4 Shipment schedule update (Northwind Traders, due 2026-10-10)
  - #9 Warehouse handover note (Bluepeak Logistics, due 2026-10-11)
  - #16 Promo campaign tracker (Acme Retail, due 2026-10-17)

Per-client summary:
            client  completed_tasks  on_time_tasks  avg_delay_days  on_time_pct
       Acme Retail                6              3             0.7         50.0
Bluepeak Logistics                5              4             0.6         80.0
 Northwind Traders                6              5             0.2         83.3

Per-owner summary:
     owner  completed_tasks  on_time_tasks  avg_delay_days  on_time_pct
  Ali Raza                5              2             1.4         40.0
Ahmed Noor                5              4             0.6         80.0
 Sara Khan                7              6            -0.3         85.7
```

Tested 2026-11-04: `python analyzer.py` exits 0 and writes both
report CSVs to `output/`.
