#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def validate_line(obj, line_no):
    if not isinstance(obj, dict):
        return f"line {line_no}: must be a JSON object"
    msgs = obj.get("messages")
    if not isinstance(msgs, list) or len(msgs) < 2:
        return f"line {line_no}: messages must be a list with >=2 items"
    roles = [m.get("role") for m in msgs if isinstance(m, dict)]
    if "user" not in roles or "assistant" not in roles:
        return f"line {line_no}: must contain user and assistant roles"
    for m in msgs:
        if not isinstance(m, dict):
            return f"line {line_no}: each message must be object"
        if m.get("role") not in {"system", "user", "assistant"}:
            return f"line {line_no}: invalid role {m.get('role')}"
        if not isinstance(m.get("content"), str) or not m.get("content").strip():
            return f"line {line_no}: content must be non-empty string"
    return None


def main():
    if len(sys.argv) != 2:
        print("usage: python3 validate_jsonl.py <file.jsonl>")
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"error: file not found: {path}")
        sys.exit(2)

    errors = []
    with path.open("r", encoding="utf-8") as f:
        for i, raw in enumerate(f, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as e:
                errors.append(f"line {i}: invalid json: {e}")
                continue
            err = validate_line(obj, i)
            if err:
                errors.append(err)

    if errors:
        print("validation failed:")
        for err in errors:
            print("-", err)
        sys.exit(1)

    print("validation passed")


if __name__ == "__main__":
    main()

