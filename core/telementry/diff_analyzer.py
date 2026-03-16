import difflib
from pathlib import Path


def compute_diff(old_snap, new_snap):
    old_path = Path(old_snap)
    new_path = Path(new_snap)

    diff_stats = {
        "files_changed": [],
        "lines_added": 0,
        "lines_removed": 0
    }

    for file in new_path.rglob("*.py"):

        relative = file.relative_to(new_path)

        old_file = old_path / relative
        new_file = new_path / relative

        if not old_file.exists():
            continue

        with open(old_file) as f1, open(new_file) as f2:
            old_lines = f1.readlines()
            new_lines = f2.readlines()

        diff = list(difflib.unified_diff(old_lines, new_lines))

        if diff:
            diff_stats["files_changed"].append(file.name)

        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                diff_stats["lines_added"] += 1
            elif line.startswith("-") and not line.startswith("---"):
                diff_stats["lines_removed"] += 1
        
        diff_stats["diff_size"] = diff_stats["lines_added"] + diff_stats["lines_removed"]
        diff_stats["files_touched_count"] = len(diff_stats["files_changed"])
    return diff_stats