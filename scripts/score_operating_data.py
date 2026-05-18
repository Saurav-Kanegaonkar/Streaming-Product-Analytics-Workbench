import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "analysis" / "outputs"


with (OUTPUTS / "summary.json").open() as handle:
    summary = json.load(handle)

with (OUTPUTS / "product_priority_queue.csv").open(newline="") as handle:
    priority_rows = list(csv.DictReader(handle))

with (OUTPUTS / "experiment_readouts.csv").open(newline="") as handle:
    experiment_rows = list(csv.DictReader(handle))

print("Streaming product analytics workbench")
print(f"Modeled rows: {summary['modeled_rows']:,}")
print(
    "Top product decision: "
    f"{summary['top_priority']['feature_name']} "
    f"({summary['top_priority']['primary_device']}), "
    f"priority={summary['top_priority']['priority_score']}"
)
print(
    "Top experiment: "
    f"{summary['top_experiment']['experiment_id']} "
    f"{summary['top_experiment']['feature_name']}, "
    f"lift={summary['top_experiment']['avg_lift_pct']}%, "
    f"decision={summary['top_experiment']['decision']}"
)
print("Highest priority queue:")
for row in priority_rows[:5]:
    print(
        f"- {row['feature_name']}: score={row['priority_score']}, "
        f"lift={row['experiment_lift_pct']}%, trust={row['data_quality_score']}, "
        f"next={row['next_move']}"
    )
print("Experiment decisions:")
for row in experiment_rows:
    print(
        f"- {row['experiment_id']} {row['feature_name']}: "
        f"{row['decision']}, p={row['min_p_value']}, "
        f"guardrail_delta={row['guardrail_delta_pct']}%"
    )
