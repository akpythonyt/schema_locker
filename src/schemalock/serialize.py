import json
import os

LOCK_VERSION = 1


def lock_path(name: str, dir: str) -> str:
    return os.path.join(dir, f"{name}.lock.json")


def write_lock(name: str, dir: str, columns: dict, generated_at: str, reason=None) -> str:
    os.makedirs(dir, exist_ok=True)
    payload = {
        "name": name,
        "version": LOCK_VERSION,
        "generated_at": generated_at,
        "reason": reason,
        "columns": columns,
    }
    path = lock_path(name, dir)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
    return path


def read_lock(name: str, dir: str) -> dict:
    path = lock_path(name, dir)
    with open(path, "r") as f:
        return json.load(f)


def lock_exists(name: str, dir: str) -> bool:
    return os.path.exists(lock_path(name, dir))
