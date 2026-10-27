import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "DT015_Data"
RESULTS = ROOT / "DT015_Results"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def make_key(os_name, path, principal, permission):
    return (
        os_name.casefold(),
        path.replace("\\", "/").casefold(),
        principal.casefold(),
        permission.casefold(),
    )


# Ket qua thuat toan
findings = read_csv(RESULTS / "Baseline_Findings.csv")

predicted = {
    make_key(r["OS"], r["Path"], r["Principal"], r["Permission"])
    for r in findings
}

# Nhan da xac nhan thu cong
known = set()

for r in read_csv(DATA / "Windows_ACL_Labels.csv"):
    if r["Label"] == "Violation":
        known.add(make_key(
            "Windows", r["Path"], r["User"], r["Permission"]
        ))

for r in read_csv(DATA / "Linux_ACL_Labels.csv"):
    if r["Label"] == "Violation":
        known.add(make_key(
            "Linux", r["Path"], r["Principal"], r["Permission"]
        ))

matched = predicted & known
unreviewed = predicted - known
missed = known - predicted

print("=== DT015 BASELINE EVALUATION ===")
print("Algorithm findings:", len(predicted))
print("Known violations:", len(known))
print("Matched violations:", len(matched))
print("Findings needing review:", len(unreviewed))
print("Known violations missed:", len(missed))

if unreviewed:
    print("Unreviewed findings:", sorted(unreviewed))

if missed:
    print("Missed violations:", sorted(missed))
