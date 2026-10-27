import csv
import json
from pathlib import Path

# Thu muc goc cua du an
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "DT015_Data"
RESULTS = ROOT / "DT015_Results"
RESULTS.mkdir(exist_ok=True)


def load_csv(filename):
    with (DATA / filename).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_json(filename):
    with (DATA / filename).open(encoding="utf-8-sig") as f:
        return json.load(f)


def matches_resource(path, resource):
    path = path.replace("\\", "/").casefold()
    resource = resource.replace("\\", "/").strip("/").casefold()
    return path.endswith("/" + resource)


findings = []

# 1. Kiem tra Windows
windows_policy = load_json("policy.json")
windows_rows = load_csv("../DT015_Tests/Windows_ACL_FullControl_Test.csv")

for row in windows_rows:
    rights = [x.strip() for x in row["Permission"].split(",")]

    if not matches_resource(row["Path"], windows_policy["resource"]):
        continue

    if row["AccessType"] != "Allow":
        continue

    if row["User"] not in windows_policy["forbidden_groups"]:
        continue

    if windows_policy["forbidden_permission"] not in rights:
        continue

    findings.append({
        "OS": "Windows",
        "Path": row["Path"],
        "Principal": row["User"],
        "Permission": row["Permission"],
        "Reason": windows_policy["reason"],
    })


# 2. Kiem tra Linux
linux_policy = load_json("Linux_ACL_Policy.json")
linux_rows = load_csv("Linux_ACL_Dataset.csv")

for row in linux_rows:
    if not matches_resource(row["Path"], linux_policy["resource"]):
        continue

    if row["ACLType"] != linux_policy["acl_type"]:
        continue

    if row["PrincipalType"] != linux_policy["principal_type"]:
        continue

    forbidden = linux_policy["forbidden_rights"]
    effective = row["EffectivePermission"]

    if not any(right in effective for right in forbidden):
        continue

    findings.append({
        "OS": "Linux",
        "Path": row["Path"],
        "Principal": row["Principal"],
        "Permission": row["Permission"],
        "Reason": linux_policy["reason"],
    })


# 3. Luu ket qua
output = RESULTS / "Baseline_FullControl_Findings.csv"

with output.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["OS", "Path", "Principal", "Permission", "Reason"]
    )
    writer.writeheader()
    writer.writerows(findings)

print("=== DT015 ACL BASELINE ===")
print("Windows findings:", sum(x["OS"] == "Windows" for x in findings))
print("Linux findings:", sum(x["OS"] == "Linux" for x in findings))
print("Total findings:", len(findings))
print("Saved:", output)
