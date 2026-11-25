"""FileWatch - a simple file integrity monitor.

Only use this tool on folders you own or have written permission to monitor.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

BASELINE_FILE = "baseline.json"


def hash_file(path, chunk_size=4096):
    """Return the SHA-256 hash of a file, or None if it can't be read."""
    sha = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                sha.update(chunk)
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"[!] Could not read {path}: {e}", file=sys.stderr)
        return None
    return sha.hexdigest()


def build_snapshot(folder):
    """Walk folder (including subfolders) -> {relative_path: hash}."""
    folder = Path(folder)
    snapshot = {}
    for path in sorted(folder.rglob("*")):
        if path.is_file():
            digest = hash_file(path)
            if digest is not None:
                snapshot[path.relative_to(folder).as_posix()] = digest
    return snapshot


def save_baseline(snapshot, baseline_path=BASELINE_FILE):
    with open(baseline_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, sort_keys=True)


def load_baseline(baseline_path=BASELINE_FILE):
    with open(baseline_path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare(old, new):
    """Compare two snapshots -> (added, modified, deleted) sorted lists."""
    old_keys, new_keys = set(old), set(new)
    added = sorted(new_keys - old_keys)
    deleted = sorted(old_keys - new_keys)
    modified = sorted(p for p in old_keys & new_keys if old[p] != new[p])
    return added, modified, deleted


def print_report(added, modified, deleted):
    if not (added or modified or deleted):
        print("No changes detected.")
        return
    for title, files in (("ADDED", added), ("MODIFIED", modified), ("DELETED", deleted)):
        print(f"\n{title} ({len(files)})")
        for f in files:
            print(f"  - {f}")
        if not files:
            print("  (none)")


def cmd_baseline(folder, baseline_path):
    snapshot = build_snapshot(folder)
    save_baseline(snapshot, baseline_path)
    print(f"Baseline saved: {len(snapshot)} files -> {baseline_path}")


def cmd_check(folder, baseline_path):
    try:
        old = load_baseline(baseline_path)
    except FileNotFoundError:
        print(f"No baseline found at {baseline_path}. Run 'baseline' first.")
        return 2
    new = build_snapshot(folder)
    added, modified, deleted = compare(old, new)
    print_report(added, modified, deleted)
    return 1 if (added or modified or deleted) else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="FileWatch - file integrity monitor")
    parser.add_argument("command", choices=["baseline", "check", "hash"])
    parser.add_argument("folder", nargs="?", default="test_folder")
    parser.add_argument("--baseline", default=BASELINE_FILE)
    args = parser.parse_args(argv)

    if args.command == "baseline":
        cmd_baseline(args.folder, args.baseline)
    elif args.command == "check":
        return cmd_check(args.folder, args.baseline)
    elif args.command == "hash":
        for name, digest in build_snapshot(args.folder).items():
            print(f"{digest}  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())