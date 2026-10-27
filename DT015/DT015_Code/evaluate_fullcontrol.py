import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "DT015_Tests"
RESULTS = ROOT / "DT015_Results"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def make_key(row):
    return (
        row["OS"].casefold(),
        row["Path"].replace("\\", "/").casefold(),
        row["Principal"].casefold(),
        row["Permission"].casefold(),
    )


# Ground truth cua bo kiem thu FullControl
labels = read_csv(TESTS / "FullControl_GroundTruth.csv")

known_violations = {
    make_key(row)
    for row in labels
    if row["Label"] == "Violation"
}

experiments = [
    ("Baseline", "Baseline_FullControl_Findings.csv"),
    ("Improved", "Improved_FullControl_Findings.csv"),
]

results = []

print("=== DT015 FULLCONTROL EVALUATION ===")
print("Known violations:", len(known_violations))

for method, filename in experiments:
    findings = read_csv(RESULTS / filename)
    predicted = {make_key(row) for row in findings}

    tp = len(predicted & known_violations)
    fn = len(known_violations - predicted)
    unreviewed = len(predicted - known_violations)

    recall = (
        tp / len(known_violations)
        if known_violations else 0
    )

    results.append({
        "Method": method,
        "TP": tp,
        "FN": fn,
        "Recall": round(recall, 4),
        "Unreviewed_Findings": unreviewed,
    })

    print(
        f"{method}: TP={tp}, FN={fn}, "
        f"Recall={recall:.2%}, "
        f"Unreviewed={unreviewed}"
    )

output = RESULTS / "Evaluation_FullControl.csv"

with output.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f, fieldnames=results[0].keys()
    )
    writer.writeheader()
    writer.writerows(results)

print("Saved:", output)
