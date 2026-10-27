import csv
import hashlib
import json
import time
from pathlib import Path
from windows_rights import violates_permission

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "DT015_Data"
TESTS = ROOT / "DT015_Tests"
RESULTS = ROOT / "DT015_Results"
LOGS = RESULTS / "logs"

RESULTS.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


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


def make_key(os_name, path, principal, permission):
    return (
        os_name.casefold(),
        path.replace("\\", "/").casefold(),
        principal.casefold(),
        permission.casefold(),
    )


# 1. Dong bang checksum cac file input & policy
input_files = {
    "windows_original_csv": DATA / "Windows_ACL_Dataset.csv",
    "linux_original_csv": DATA / "Linux_ACL_Dataset.csv",
    "windows_fullcontrol_csv": TESTS / "Windows_ACL_FullControl_Test.csv",
    "windows_noviolation_csv": TESTS / "Windows_ACL_NoViolation_Test.csv",
    "linux_noviolation_csv": TESTS / "Linux_ACL_NoViolation_Test.csv",
    "windows_policy_json": DATA / "policy.json",
    "linux_policy_json": DATA / "Linux_ACL_Policy.json",
    "fullcontrol_groundtruth_csv": TESTS / "FullControl_GroundTruth.csv",
}

checksum_manifest = {
    "seed": "not applicable (deterministic rule-based model)",
    "controlled_runs": 3,
    "files": {
        name: {
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256_file(path),
        }
        for name, path in input_files.items()
    },
}

checksum_path = RESULTS / "Experiment_Input_Checksums.json"
with checksum_path.open("w", encoding="utf-8") as f:
    json.dump(checksum_manifest, f, indent=2, ensure_ascii=False)

windows_policy = load_json(DATA / "policy.json")
linux_policy = load_json(DATA / "Linux_ACL_Policy.json")

# Ground truth 3 vi pham cho Kich ban A (Original) va Kich ban B (FullControl)
gt_original = {
    make_key("Windows", r"D:\A.monhoc\BC_AT_BMHTTT\DT015_Lab\Confidential\salary.txt", "Everyone", "Modify, Synchronize"),
    make_key("Windows", r"D:\A.monhoc\BC_AT_BMHTTT\DT015_Lab\Confidential\salary.txt", r"NT AUTHORITY\Authenticated Users", "Modify, Synchronize"),
    make_key("Linux", "/home/truong_tam_dt015/dt015_lab/Confidential/salary.txt", "OTHER", "rw-"),
}

gt_fullcontrol = {
    make_key(r["OS"], r["Path"], r["Principal"], r["Permission"])
    for r in load_csv(TESTS / "FullControl_GroundTruth.csv")
    if r["Label"] == "Violation"
}

scenarios = [
    {
        "name": "Scenario_A_Original_Lab",
        "win_csv": DATA / "Windows_ACL_Dataset.csv",
        "lin_csv": DATA / "Linux_ACL_Dataset.csv",
        "known_set": gt_original,
    },
    {
        "name": "Scenario_B_FullControl_Test",
        "win_csv": TESTS / "Windows_ACL_FullControl_Test.csv",
        "lin_csv": DATA / "Linux_ACL_Dataset.csv",
        "known_set": gt_fullcontrol,
    },
    {
        "name": "Scenario_C_NoViolation_Test",
        "win_csv": TESTS / "Windows_ACL_NoViolation_Test.csv",
        "lin_csv": TESTS / "Linux_ACL_NoViolation_Test.csv",
        "known_set": set(),
    },
]


def run_detector(win_rows, lin_rows, mode):
    findings = []
    for row in win_rows:
        if not matches_resource(row["Path"], windows_policy["resource"]):
            continue
        if row["AccessType"] != "Allow":
            continue
        if row["User"] not in windows_policy["forbidden_groups"]:
            continue

        if mode == "Baseline":
            rights = [x.strip() for x in row["Permission"].split(",")]
            violated = windows_policy["forbidden_permission"] in rights
        else:
            violated = violates_permission(
                row["Permission"], windows_policy["forbidden_permission"]
            )

        if violated:
            findings.append({
                "OS": "Windows",
                "Path": row["Path"],
                "Principal": row["User"],
                "Permission": row["Permission"],
                "Reason": windows_policy["reason"],
            })

    for row in lin_rows:
        if not matches_resource(row["Path"], linux_policy["resource"]):
            continue
        if row["ACLType"] != linux_policy["acl_type"]:
            continue
        if row["PrincipalType"] != linux_policy["principal_type"]:
            continue

        forbidden = linux_policy["forbidden_rights"]
        effective = row["EffectivePermission"]
        if any(right in effective for right in forbidden):
            findings.append({
                "OS": "Linux",
                "Path": row["Path"],
                "Principal": row["Principal"],
                "Permission": row["Permission"],
                "Reason": linux_policy["reason"],
            })
    return findings


all_run_rows = []

for run_id in range(1, 4):
    log_lines = [
        f"=== DT015 CONTROLLED EXPERIMENT RUN {run_id}/3 ===",
        "seed: not applicable (deterministic rule-based model)",
        f"checksum_manifest: {checksum_path.name}",
    ]

    for sc in scenarios:
        win_rows = load_csv(sc["win_csv"])
        lin_rows = load_csv(sc["lin_csv"])
        known_set = sc["known_set"]

        t0 = time.perf_counter()
        base_findings = run_detector(win_rows, lin_rows, "Baseline")
        t_base_ms = (time.perf_counter() - t0) * 1000.0

        t1 = time.perf_counter()
        imp_findings = run_detector(win_rows, lin_rows, "Improved")
        t_imp_ms = (time.perf_counter() - t1) * 1000.0

        base_pred = {make_key(x["OS"], x["Path"], x["Principal"], x["Permission"]) for x in base_findings}
        imp_pred = {make_key(x["OS"], x["Path"], x["Principal"], x["Permission"]) for x in imp_findings}

        base_tp = len(base_pred & known_set)
        base_fn = len(known_set - base_pred)
        base_fp = len(base_pred - known_set)

        imp_tp = len(imp_pred & known_set)
        imp_fn = len(known_set - imp_pred)
        imp_fp = len(imp_pred - known_set)

        row_record = {
            "Run": run_id,
            "Scenario": sc["name"],
            "Windows rows": len(win_rows),
            "Linux rows": len(lin_rows),
            "Known violations": len(known_set),
            "Baseline findings": len(base_findings),
            "Improved findings": len(imp_findings),
            "TP": f"Base:{base_tp} | Imp:{imp_tp}",
            "FN": f"Base:{base_fn} | Imp:{imp_fn}",
            "FP reviewed": f"Base:{base_fp} | Imp:{imp_fp}",
            "Time": f"Base:{t_base_ms:.3f}ms | Imp:{t_imp_ms:.3f}ms",
        }
        all_run_rows.append(row_record)

        log_lines.append(
            f"[{sc['name']}] Win={len(win_rows)}, Lin={len(lin_rows)}, Known={len(known_set)} | "
            f"Baseline: findings={len(base_findings)}, TP={base_tp}, FN={base_fn}, FP_reviewed={base_fp}, time={t_base_ms:.3f}ms | "
            f"Improved: findings={len(imp_findings)}, TP={imp_tp}, FN={imp_fn}, FP_reviewed={imp_fp}, time={t_imp_ms:.3f}ms"
        )

    log_file = LOGS / f"run_{run_id}.log"
    log_file.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

# Luu chi tiet 3 luot chay
detail_csv = RESULTS / "Experiment_Runs_Detail.csv"
with detail_csv.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(all_run_rows[0].keys()))
    writer.writeheader()
    writer.writerows(all_run_rows)

# Luu bang ma tran 3 kich ban (lay luot 1 lam dai dien sau khi kiem tra 3 luot on dinh 100%)
summary_rows = [{k: v for k, v in r.items() if k != "Run"} for r in all_run_rows if r["Run"] == 1]
summary_csv = RESULTS / "Experiment_Matrix_Summary.csv"
with summary_csv.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
    writer.writeheader()
    writer.writerows(summary_rows)

print("=== DT015 EXPERIMENT MATRIX (3 SCENARIOS x 3 RUNS) COMPLETED ===")
for r in summary_rows:
    print(r)
print("\nSaved Checksums:", checksum_path)
print("Saved 3 Logs in:", LOGS)
print("Saved Detail CSV:", detail_csv)
print("Saved Summary Matrix CSV:", summary_csv)
