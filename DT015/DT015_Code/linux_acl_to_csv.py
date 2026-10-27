import csv
import sys
from pathlib import Path

source = Path(sys.argv[1])
output = Path(sys.argv[2])

rows = []
path = ""
owner = ""
group = ""

for line in source.read_text(encoding="utf-8").splitlines():
    if line.startswith("# file: "):
        path = line.removeprefix("# file: ")
        owner = ""
        group = ""
    elif line.startswith("# owner: "):
        owner = line.removeprefix("# owner: ")
    elif line.startswith("# group: "):
        group = line.removeprefix("# group: ")
    elif path and line and not line.startswith("#"):
        entry, _, comment = line.partition("#")
        entry = entry.strip()

        acl_type = "Default" if entry.startswith("default:") else "Access"

        if acl_type == "Default":
            entry = entry.removeprefix("default:")

        parts = entry.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid ACL entry: {line}")

        principal_type, name, permission = parts

        names = {
            "user": "OWNER",
            "group": "OWNING_GROUP",
            "other": "OTHER",
            "mask": "MASK",
        }

        principal = name or names.get(principal_type, "")

        effective = permission
        if "effective:" in comment:
            effective = comment.split("effective:", 1)[1].strip()

        rows.append({
            "OS": "Linux",
            "Path": path,
            "Owner": owner,
            "Group": group,
            "ACLType": acl_type,
            "PrincipalType": principal_type,
            "Principal": principal,
            "Permission": permission,
            "EffectivePermission": effective,
        })

columns = [
    "OS", "Path", "Owner", "Group", "ACLType",
    "PrincipalType", "Principal", "Permission",
    "EffectivePermission"
]

with output.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print(f"Exported {len(rows)} ACL entries")
print(f"Saved to: {output}")
