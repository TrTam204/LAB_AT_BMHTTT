import csv
import json
from pathlib import Path
from windows_rights import violates_permission

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "DT015_Data"
TESTS = ROOT / "DT015_Tests"
RESULTS = ROOT / "DT015_Results"
RESULTS.mkdir(exist_ok=True)


def load_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_json(path):
    with path.open(encoding="utf-8-sig") as f:
        return json.load(f)


def matches_resource(path, resource):
    path = path.replace("\\", "/").casefold()
    resource = resource.replace("\\", "/").strip("/").casefold()
    return path.endswith("/" + resource)


windows_policy = load_json(DATA / "policy.json")
linux_policy = load_json(DATA / "Linux_ACL_Policy.json")

windows_rows = load_csv(TESTS / "Windows_ACL_NoViolation_Test.csv")
linux_rows = load_csv(TESTS / "Linux_ACL_NoViolation_Test.csv")


def run_audit(mode):
    findings = []

    # 1. Kiem tra Windows
    for row in windows_rows:
        if not matches_resource(row["Path"], windows_policy["resource"]):
            continue
        if row["AccessType"] != "Allow":
            continue
        if row["User"] not in windows_policy["forbidden_groups"]:
            continue

        if mode == "Baseline":
            rights = [x.strip() for x in row["Permission"].split(",")]
            is_violation = windows_policy["forbidden_permission"] in rights
        else:
            is_violation = violates_permission(
                row["Permission"], windows_policy["forbidden_permission"]
            )

        if not is_violation:
            continue

        findings.append({
            "OS": "Windows",
            "Path": row["Path"],
            "Principal": row["User"],
            "Permission": row["Permission"],
            "Reason": windows_policy["reason"],
        })

    # 2. Kiem tra Linux
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

    output = RESULTS / f"{mode}_NoViolation_Findings.csv"
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["OS", "Path", "Principal", "Permission", "Reason"]
        )
        writer.writeheader()
        writer.writerows(findings)

    win_count = sum(x["OS"] == "Windows" for x in findings)
    lin_count = sum(x["OS"] == "Linux" for x in findings)
    print(f"=== DT015 NO_VIOLATION TEST ({mode.upper()}) ===")
    print("Windows rows scanned:", len(windows_rows))
    print("Linux rows scanned:", len(linux_rows))
    print("Windows findings:", win_count)
    print("Linux findings:", lin_count)
    print("Total findings:", len(findings))
    print("Saved:", output)
    print()


run_audit("Baseline")
run_audit("Improved")
