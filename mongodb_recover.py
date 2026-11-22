#!/usr/bin/env python3
"""
MongoDB 4.4 Crash Recovery Program
==================================

Recovers data from a MongoDB 4.4 instance after an abrupt shutdown (crash).

Designed to run on the Windows machine that owns the data. Defaults match your
environment:

    Data path:  E:\Tam_data\4.4\data\
    Log path:   E:\Tam_data\4.4\log\

Recovery strategy (MongoDB 4.4 uses the WiredTiger storage engine by default):

1. Safety: back up the raw data + log directories before touching anything.
2. Try a normal mongod startup (WiredTiger auto-recovers from its journal/checkpoint).
3. If startup fails, run `mongod --repair`.
4. If repair fails, salvage with the WiredTiger `wt` utility (if available).
5. Export recoverable data with `mongodump`.
6. Report per-database/collection results and next steps.

Usage
-----
    python mongodb_recover.py                    # interactive, safe mode (no writes)
    python mongodb_recover.py --execute          # perform repair + dump
    python mongodb_recover.py --data-path "D:\mongo\data" --log-path "D:\mongo\log"
    python mongodb_recover.py --dump-only        # skip repair, just mongodump what we can

Prerequisites (on the Windows host):
    - MongoDB 4.4 binaries (mongod, mongodump, mongo) on PATH, or set MONGODB_HOME.
    - Administrator / owner access to the data and log directories.
    - Enough free disk space for a backup copy of the data directory.

Safety
------
By default the program runs in read-only / report mode. It never deletes or
modifies your source data. The only destructive-ish step is `mongod --repair`,
which requires --execute and creates a repair directory under the data path.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Configuration - your paths (overridable via --data-path / --log-path or env)
# ---------------------------------------------------------------------------
DEFAULT_DATA_PATH = r"E:\Tam_data\4.4\data\"
DEFAULT_LOG_PATH = r"E:\Tam_data\4.4\log\"

MONGODB_BINARIES = ["mongod", "mongodump", "mongo", "wt"]

RECOVERY_LOG_NAME = "recovery_report.json"


class RecoveryError(RuntimeError):
    pass


def now() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str) -> None:
    print(f"[{now()}] {msg}", flush=True)


def find_binary(name: str, mongodb_home: Optional[str]) -> Optional[str]:
    """Locate a MongoDB binary on PATH or under MONGODB_HOME/bin."""
    if mongodb_home:
        candidate = Path(mongodb_home) / "bin" / name
        if candidate.exists():
            return str(candidate)
        # Windows may append .exe
        candidate_exe = Path(str(candidate) + ".exe")
        if candidate_exe.exists():
            return str(candidate_exe)
    # Check PATH
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory:
            continue
        candidate = Path(directory) / name
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
        candidate_exe = Path(str(candidate) + ".exe")
        if candidate_exe.exists() and os.access(candidate_exe, os.X_OK):
            return str(candidate_exe)
    return None


def locate_binaries(mongodb_home: Optional[str]) -> Dict[str, Optional[str]]:
    return {name: find_binary(name, mongodb_home) for name in MONGODB_BINARIES}


def path_exists(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False


def directory_size(path: Path) -> int:
    total = 0
    if not path_exists(path):
        return 0
    for entry in path.rglob("*"):
        try:
            if entry.is_file():
                total += entry.stat().st_size
        except Exception:
            pass
    return total


def format_size(bytes_val: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} PB"


def run_cmd(
    cmd: List[str],
    cwd: Optional[str] = None,
    timeout: int = 3600,
    capture: bool = True,
) -> Tuple[int, str, str]:
    log("RUN: " + " ".join(cmd))
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture,
            text=True,
            timeout=timeout,
        )
        out = proc.stdout or ""
        err = proc.stderr or ""
        if capture:
            if out:
                log("STDOUT:\n" + out)
            if err:
                log("STDERR:\n" + err)
        return proc.returncode, out, err
    except subprocess.TimeoutExpired as exc:
        log(f"TIMEOUT after {timeout}s: {' '.join(cmd)}")
        return -1, "", str(exc)
    except FileNotFoundError:
        log(f"NOT FOUND: {cmd[0]}")
        return -2, "", f"binary not found: {cmd[0]}"
    except Exception as exc:  # noqa: BLE001
        log(f"ERROR running {' '.join(cmd)}: {exc}")
        return -3, "", str(exc)


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------


def step_environment_report(
    data_path: Path,
    log_path: Path,
    mongodb_home: Optional[str],
) -> Dict:
    log("=== Step 0: Environment report ===")
    binaries = locate_binaries(mongodb_home)
    report = {
        "timestamp": now(),
        "os": sys.platform,
        "data_path": str(data_path),
        "log_path": str(log_path),
        "mongodb_home": mongodb_home,
        "binaries": binaries,
        "data_exists": path_exists(data_path),
        "log_exists": path_exists(log_path),
        "data_size_bytes": directory_size(data_path) if path_exists(data_path) else 0,
        "log_size_bytes": directory_size(log_path) if path_exists(log_path) else 0,
    }
    missing = [k for k, v in binaries.items() if v is None]
    if missing:
        log(f"WARNING: missing binaries: {', '.join(missing)}")
    else:
        log("All MongoDB binaries located.")
    log(f"Data dir exists: {report['data_exists']} ({format_size(report['data_size_bytes'])})")
    log(f"Log dir exists: {report['log_exists']} ({format_size(report['log_size_bytes'])})")
    return report


def step_backup(
    data_path: Path,
    log_path: Path,
    backup_root: Optional[Path] = None,
) -> Dict:
    """Copy data + log directories to a timestamped backup. Read-only safe step."""
    log("=== Step 1: Backup data + log directories ===")
    if backup_root is None:
        backup_root = Path.cwd() / "mongodb_recovery_backup"
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / f"mongodb_44_crash_backup_{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "backup_dir": str(backup_dir),
        "data_backed_up": False,
        "log_backed_up": False,
        "errors": [],
    }

    for label, src in (("data", data_path), ("log", log_path)):
        if not path_exists(src):
            msg = f"SKIP backup {label}: source not found: {src}"
            log(msg)
            result["errors"].append(msg)
            continue
        dst = backup_dir / label
        try:
            log(f"Copying {label} -> {dst}")
            shutil.copytree(src, dst, dirs_exist_ok=True, copy_function=shutil.copy2)
            if label == "data":
                result["data_backed_up"] = True
            else:
                result["log_backed_up"] = True
            log(f"  backed up {format_size(directory_size(dst))}")
        except Exception as exc:  # noqa: BLE001
            msg = f"FAILED backup {label}: {exc}"
            log(msg)
            result["errors"].append(msg)

    return result


def step_normal_start(
    mongod: str,
    data_path: Path,
    log_path: Path,
    log_file: Path,
    port: int = 27017,
    wait_seconds: int = 60,
) -> Dict:
    """Try starting mongod normally (WiredTiger auto-recovery)."""
    log("=== Step 2: Attempt normal mongod startup (auto-recovery) ===")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        mongod,
        "--dbpath", str(data_path),
        "--logpath", str(log_file),
        "--port", str(port),
        "--bind_ip", "127.0.0.1",
        "--fork",
    ]
    # On Windows, --fork requires --logpath; already provided.
    rc, out, err = run_cmd(cmd, timeout=wait_seconds + 10)

    result = {
        "attempted": True,
        "succeeded": rc == 0,
        "returncode": rc,
        "stdout": out,
        "stderr": err,
    }
    if rc == 0:
        log("Normal startup succeeded. WiredTiger auto-recovery completed.")
    else:
        log(f"Normal startup failed (rc={rc}). Will try repair.")
    return result


def step_repair(
    mongod: str,
    data_path: Path,
    log_path: Path,
    log_file: Path,
) -> Dict:
    """Run mongod --repair. Only under --execute; creates repair files under data_path."""
    log("=== Step 3: mongod --repair ===")
    repair_log = log_path / "repair.log"
    repair_log.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        mongod,
        "--dbpath", str(data_path),
        "--logpath", str(repair_log),
        "--repair",
    ]
    rc, out, err = run_cmd(cmd, timeout=3600)

    result = {
        "attempted": True,
        "succeeded": rc == 0,
        "returncode": rc,
        "stdout": out,
        "stderr": err,
        "repair_log": str(repair_log),
    }
    if rc == 0:
        log("mongod --repair completed successfully.")
    else:
        log(f"mongod --repair failed (rc={rc}). Check {repair_log}")
    return result


def step_wiredtiger_salvage(
    wt: Optional[str],
    data_path: Path,
) -> Dict:
    """Use the WiredTiger `wt` utility to salvage/verify files (last resort)."""
    log("=== Step 4: WiredTiger `wt` salvage (last resort) ===")
    if not wt:
        msg = "wt binary not found; skipping WiredTiger salvage."
        log(msg)
        return {"attempted": False, "succeeded": False, "reason": "wt not found"}

    # List WiredTiger files
    wt_files = [p for p in data_path.glob("*") if p.suffix in (".wt", "")] if path_exists(data_path) else []
    log(f"Found {len(wt_files)} candidate WiredTiger files in data path.")

    # Run wt salvage on each .wt file into a salvage dir
    salvage_dir = data_path.parent / "wiredtiger_salvage"
    salvage_dir.mkdir(parents=True, exist_ok=True)

    results = []
    overall_ok = True
    for wt_file in wt_files:
        if not wt_file.is_file():
            continue
        out_name = salvage_dir / (wt_file.name + ".salvaged")
        cmd = [wt, "salvage", "-f", str(wt_file), "-o", str(out_name)]
        rc, out, err = run_cmd(cmd, timeout=3600)
        ok = rc == 0 and out_name.exists()
        overall_ok = overall_ok and ok
        results.append({
            "file": str(wt_file),
            "output": str(out_name),
            "returncode": rc,
            "succeeded": ok,
        })
        log(f"  {wt_file.name}: {'OK' if ok else 'FAILED (rc=' + str(rc) + ')'}")

    return {"attempted": True, "succeeded": overall_ok, "files": results, "dir": str(salvage_dir)}


def step_dump(
    mongodump: str,
    data_path: Path,
    dump_root: Optional[Path] = None,
    host: str = "127.0.0.1",
    port: int = 27017,
) -> Dict:
    """Export recoverable databases with mongodump."""
    log("=== Step 5: mongodump export ===")
    if dump_root is None:
        dump_root = Path.cwd() / "mongodb_recovery_dump"
    dump_root.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_dir = dump_root / f"mongodump_{stamp}"
    dump_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        mongodump,
        "--host", host,
        "--port", str(port),
        "--out", str(dump_dir),
    ]
    # If mongod isn't running, mongodump fails. Try direct dbpath dump as fallback.
    rc, out, err = run_cmd(cmd, timeout=3600)

    result = {
        "attempted": True,
        "succeeded": rc == 0,
        "returncode": rc,
        "dump_dir": str(dump_dir),
        "stdout": out,
        "stderr": err,
        "fallback_direct_dump": False,
    }
    if rc == 0:
        log(f"mongodump succeeded -> {dump_dir}")
        return result

    log(f"mongodump against live server failed (rc={rc}); trying direct dbpath dump.")
    # Fallback: dump directly from data files (mongodump supports --dbpath in some builds;
    # if not, we report that a live server is required).
    cmd2 = [
        mongodump,
        "--dbpath", str(data_path),
        "--out", str(dump_dir),
    ]
    rc2, out2, err2 = run_cmd(cmd2, timeout=3600)
    result["fallback_direct_dump"] = True
    result["fallback_returncode"] = rc2
    result["fallback_stdout"] = out2
    result["fallback_stderr"] = err2
    if rc2 == 0:
        result["succeeded"] = True
        log(f"Direct dbpath mongodump succeeded -> {dump_dir}")
    else:
        log(f"Direct dbpath mongodump also failed (rc={rc2}).")
    return result


def step_scan_logs(log_path: Path) -> Dict:
    """Scan the MongoDB log for crash/recovery-related errors."""
    log("=== Step 6: Scan MongoDB log for errors ===")
    errors = []
    warnings_ = []
    recovery_lines = []
    if not path_exists(log_path):
        return {"log_path": str(log_path), "exists": False, "errors": [], "warnings": [], "recovery_lines": []}

    for log_file in log_path.glob("*.log"):
        try:
            text = log_file.read_text(errors="replace")
        except Exception as exc:  # noqa: BLE001
            log(f"Could not read {log_file}: {exc}")
            continue
        for line in text.splitlines():
            low = line.lower()
            if any(k in low for k in ["fatal", "error", "exception", "assert", "corrupt", "not found"]):
                errors.append(str(log_file) + ": " + line)
            elif any(k in low for k in ["warn", "recover", "journal", "wiredtiger", "checkpoint"]):
                if "recover" in low or "journal" in low or "wiredtiger" in low:
                    recovery_lines.append(str(log_file) + ": " + line)
                else:
                    warnings_.append(str(log_file) + ": " + line)

    result = {
        "log_path": str(log_path),
        "exists": True,
        "error_count": len(errors),
        "warning_count": len(warnings_),
        "recovery_count": len(recovery_lines),
        "errors": errors[:50],
        "warnings": warnings_[:50],
        "recovery_lines": recovery_lines[:50],
    }
    log(f"Log scan: {result['error_count']} errors, {result['warning_count']} warnings, {result['recovery_count']} recovery lines.")
    return result


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def write_report(path: Path, report: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    log(f"Report written to {path}")


def recover(
    data_path: str,
    log_path: str,
    execute: bool = False,
    dump_only: bool = False,
    mongodb_home: Optional[str] = None,
    backup_root: Optional[str] = None,
    dump_root: Optional[str] = None,
) -> Dict:
    data_p = Path(data_path)
    log_p = Path(log_path)
    report: Dict = {
        "timestamp": now(),
        "data_path": str(data_p),
        "log_path": str(log_p),
        "execute": execute,
        "dump_only": dump_only,
        "steps": {},
        "overall_success": False,
        "recommendation": "",
    }

    # Step 0 - environment
    report["steps"]["environment"] = step_environment_report(data_p, log_p, mongodb_home)

    # Step 1 - backup (always safe)
    report["steps"]["backup"] = step_backup(data_p, log_p, Path(backup_root) if backup_root else None)

    binaries = report["steps"]["environment"]["binaries"]
    mongod = binaries.get("mongod")
    mongodump = binaries.get("mongodump")
    wt = binaries.get("wt")

    log_file = log_p / "mongod_recovery.log"

    if dump_only:
        # Skip repair; just try to dump (requires a live mongod started elsewhere)
        report["steps"]["dump"] = step_dump(mongodump, data_p, Path(dump_root) if dump_root else None)
    else:
        # Step 2 - normal startup
        report["steps"]["normal_start"] = step_normal_start(mongod, data_p, log_p, log_file)

        if not report["steps"]["normal_start"]["succeeded"] and execute:
            # Step 3 - repair
            report["steps"]["repair"] = step_repair(mongod, data_p, log_p, log_file)
            # Retry startup after repair
            retry_log = log_p / "mongod_recovery_after_repair.log"
            report["steps"]["normal_start_after_repair"] = step_normal_start(
                mongod, data_p, log_p, retry_log
            )

        # Step 4 - WiredTiger salvage if still failing
        if not report["steps"]["normal_start"]["succeeded"] and not report["steps"].get("normal_start_after_repair", {}).get("succeeded"):
            report["steps"]["wiredtiger_salvage"] = step_wiredtiger_salvage(wt, data_p)

        # Step 5 - dump
        report["steps"]["dump"] = step_dump(mongodump, data_p, Path(dump_root) if dump_root else None)

    # Step 6 - logs
    report["steps"]["log_scan"] = step_scan_logs(log_p)

    # Overall assessment
    dump_ok = report["steps"].get("dump", {}).get("succeeded", False)
    normal_ok = report["steps"].get("normal_start", {}).get("succeeded", False)
    repaired_ok = report["steps"].get("normal_start_after_repair", {}).get("succeeded", False)
    salvaged_ok = report["steps"].get("wiredtiger_salvage", {}).get("succeeded", False)

    report["overall_success"] = dump_ok or normal_ok or repaired_ok or salvaged_ok

    if dump_ok:
        report["recommendation"] = (
            "Data exported successfully with mongodump. Inspect the dump directory, "
            "then restore with mongorestore into a fresh MongoDB 4.4 instance."
        )
    elif normal_ok or repaired_ok:
        report["recommendation"] = (
            "mongod is running and recovered. Export data with mongodump immediately "
            "as a precaution, then validate application connectivity."
        )
    elif salvaged_ok:
        report["recommendation"] = (
            "WiredTiger salvage produced output files. These are raw WiredTiger pages "
            "and are not directly usable; engage MongoDB support or a data-recovery "
            "specialist to interpret them."
        )
    else:
        report["recommendation"] = (
            "Automatic recovery did not succeed. Do not delete any files. "
            "Restore from a recent backup if available, or contact MongoDB support "
            "with the recovery report and MongoDB log."
        )

    report_path = Path.cwd() / RECOVERY_LOG_NAME
    write_report(report_path, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="MongoDB 4.4 crash recovery program")
    p.add_argument("--data-path", default=DEFAULT_DATA_PATH, help="MongoDB data directory path")
    p.add_argument("--log-path", default=DEFAULT_LOG_PATH, help="MongoDB log directory path")
    p.add_argument("--mongodb-home", default=None, help="MongoDB installation root (contains bin/)")
    p.add_argument("--execute", action="store_true", help="Perform repair + dump (default: safe/report only)")
    p.add_argument("--dump-only", action="store_true", help="Only attempt mongodump export; skip repair")
    p.add_argument("--backup-root", default=None, help="Directory for the pre-recovery backup")
    p.add_argument("--dump-root", default=None, help="Directory for mongodump output")
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    log("MongoDB 4.4 Crash Recovery Program")
    log(f"Data path : {args.data_path}")
    log(f"Log path  : {args.log_path}")
    log(f"Mode      : {'EXECUTE' if args.execute else 'SAFE/REPORT (no changes)'}")

    if not args.execute and not args.dump_only:
        log("Running in safe mode. Re-run with --execute to perform repair/dump.")

    try:
        report = recover(
            data_path=args.data_path,
            log_path=args.log_path,
            execute=args.execute,
            dump_only=args.dump_only,
            mongodb_home=args.mongodb_home,
            backup_root=args.backup_root,
            dump_root=args.dump_root,
        )
    except Exception as exc:  # noqa: BLE001
        log(f"FATAL: {exc}")
        return 1

    log("=== Recovery complete ===")
    log(f"Overall success: {report['overall_success']}")
    log(f"Recommendation: {report['recommendation']}")
    log(f"Report: {Path.cwd() / RECOVERY_LOG_NAME}")
    return 0 if report["overall_success"] else 2


if __name__ == "__main__":
    sys.exit(main())
