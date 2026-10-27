import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "DT015_Data"
TESTS = ROOT / "DT015_Tests"
TESTS.mkdir(exist_ok=True)


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def save_csv(path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


# Windows: thay quyen Modify cua hai nhom bi cam
columns, windows = read_csv(DATA / "Windows_ACL_Dataset.csv")

windows_changed = 0

for row in windows:
    path = row["Path"].replace("\\", "/").casefold()

    if (
        path.endswith("/confidential/salary.txt")
        and row["User"] in (
            "Everyone",
            "NT AUTHORITY\\Authenticated Users",
        )
        and row["AccessType"] == "Allow"
        and "Modify" in row["Permission"]
    ):
        row["Permission"] = "ReadAndExecute, Synchronize"
        windows_changed += 1

if windows_changed != 2:
    raise SystemExit("ERROR: Expected 2 Windows changes")

save_csv(
    TESTS / "Windows_ACL_NoViolation_Test.csv",
    columns,
    windows,
)

# Linux: bo quyen doc/ghi cua OTHER tren salary.txt
columns, linux = read_csv(DATA / "Linux_ACL_Dataset.csv")

linux_changed = 0

for row in linux:
    path = row["Path"].replace("\\", "/").casefold()

    if (
        path.endswith("/confidential/salary.txt")
        and row["ACLType"] == "Access"
        and row["PrincipalType"] == "other"
    ):
        row["Permission"] = "---"
        row["EffectivePermission"] = "---"
        linux_changed += 1

if linux_changed != 1:
    raise SystemExit("ERROR: Expected 1 Linux change")

save_csv(
    TESTS / "Linux_ACL_NoViolation_Test.csv",
    columns,
    linux,
)

print("=== DT015 NO-VIOLATION TEST DATA ===")
print("Windows records:", len(windows))
print("Windows test changes:", windows_changed)
print("Linux records:", len(linux))
print("Linux test changes:", linux_changed)
print("Original datasets: unchanged")
print("Test files: created")
