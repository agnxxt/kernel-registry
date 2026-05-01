#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git_output(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def changed_schema_files(base_ref: str):
    out = git_output(["git", "diff", "--name-only", f"{base_ref}...HEAD", "--", "schemas/**/*.json"])
    return [Path(p) for p in out.splitlines() if p]


def load_json_from_git(ref: str, path: Path):
    try:
        txt = subprocess.check_output(["git", "show", f"{ref}:{path.as_posix()}"], cwd=ROOT, text=True)
    except subprocess.CalledProcessError:
        return None
    return json.loads(txt)


def walk_required(schema, prefix=""):
    req = set()
    if isinstance(schema, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                req.add(f"{prefix}.{key}" if prefix else key)
        props = schema.get("properties", {})
        if isinstance(props, dict):
            for k, v in props.items():
                pfx = f"{prefix}.{k}" if prefix else k
                req |= walk_required(v, pfx)
    return req


def walk_enums(schema, prefix=""):
    enums = {}
    if isinstance(schema, dict):
        if "enum" in schema and isinstance(schema["enum"], list):
            enums[prefix or "$"] = set(map(str, schema["enum"]))
        props = schema.get("properties", {})
        if isinstance(props, dict):
            for k, v in props.items():
                pfx = f"{prefix}.{k}" if prefix else k
                enums.update(walk_enums(v, pfx))
    return enums


def main():
    base_ref = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    files = changed_schema_files(base_ref)
    failures = []

    for rel in files:
        new_path = ROOT / rel
        if not new_path.exists():
            continue
        old = load_json_from_git(base_ref, rel)
        if old is None:
            continue
        new = json.loads(new_path.read_text())

        old_required = walk_required(old)
        new_required = walk_required(new)
        removed_required = sorted(old_required - new_required)
        if removed_required:
            failures.append(f"{rel}: removed required fields: {', '.join(removed_required)}")

        old_enums = walk_enums(old)
        new_enums = walk_enums(new)
        for field, old_values in old_enums.items():
            if field not in new_enums:
                failures.append(f"{rel}: removed enum field {field}")
                continue
            removed_values = sorted(old_values - new_enums[field])
            if removed_values:
                failures.append(f"{rel}: enum narrowed at {field}, removed {removed_values}")

    if failures:
        print("JSON schema compatibility check failed:")
        for f in failures:
            print(f" - {f}")
        return 1

    print("JSON schema compatibility checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
