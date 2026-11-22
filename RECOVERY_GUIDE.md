# MongoDB 4.4 Crash Recovery Guide

Recovers data from MongoDB 4.4 after an abrupt shutdown (crash).

Your environment:

- Data path:  `E:\Tam_data\4.4\data\`
- Log path:   `E:\Tam_data\4.4\log\`

## How MongoDB 4.4 recovers after a crash

MongoDB 4.4 uses the **WiredTiger** storage engine by default. WiredTiger is crash-safe:
it writes to a write-ahead journal and checkpoints data files periodically. On restart,
`mongod` replays the journal since the last checkpoint and brings the database to a
consistent state automatically. In most crash cases, simply starting `mongod` is enough.

## Files included

| File | Purpose |
|------|---------|
| `mongodb_recover.py` | Cross-platform Python recovery program |
| `mongodb_recover.ps1` | PowerShell wrapper for Windows |
| `RECOVERY_GUIDE.md` | This guide |

## Prerequisites (on the Windows host)

- MongoDB 4.4 installed; `mongod`, `mongodump`, and `mongo` on `PATH`, or set `MONGODB_HOME`
  to the installation root (the folder that contains `bin\`).
- Python 3 (to run the recovery program).
- Administrator / owner access to `E:\Tam_data\4.4\data\` and `E:\Tam_data\4.4\log\`.
- Free disk space roughly equal to the size of the data directory (for the safety backup).

## Run the recovery

Open PowerShell as Administrator in the folder containing these files:

```powershell
# 1. Safe mode - inspect, back up, report (no changes to source data)
.\mongodb_recover.ps1

# 2. If startup fails, perform repair + dump
.\mongodb_recover.ps1 -Execute

# 3. Only export what is readable (skip repair)
.\mongodb_recover.ps1 -Execute -DumpOnly

# 4. Custom paths
.\mongodb_recover.ps1 -DataPath "D:\mongo\data" -LogPath "D:\mongo\log" -Execute
```

Or run the Python program directly:

```powershell
python mongodb_recover.py               # safe mode
python mongodb_recover.py --execute     # repair + dump
python mongodb_recover.py --dump-only   # export only
```

## What the program does

1. **Environment report** - locates `mongod`/`mongodump`/`wt`, checks data & log dirs.
2. **Safety backup** - copies `data\` and `log\` to a timestamped backup folder before any
   modification. Never deletes or overwrites your source files.
3. **Normal startup** - starts `mongod`; WiredTiger auto-recovery from journal/checkpoint.
4. **`mongod --repair`** - if startup fails and `--execute` is given, runs the repair utility.
5. **WiredTiger `wt` salvage** - last-resort salvage of `.wt` files if repair also fails.
6. **`mongodump`** - exports recoverable databases to a dump folder.
7. **Log scan** - parses the MongoDB log for fatal/error/recovery messages.
8. **Report** - writes `recovery_report.json` with per-step results and a recommendation.

## After recovery

- If `mongodump` succeeded: restore into a fresh MongoDB 4.4 instance with `mongorestore`,
  then validate your application data.
- If `mongod` is running: export data with `mongodump` immediately as a precaution.
- If nothing succeeded: **do not delete any files**. Restore from a recent backup if you
  have one, or contact MongoDB support with `recovery_report.json` and the MongoDB log.

## Safety rules

- Never delete journal files (`journal/`), `.wt` files, or the `diagnostic.data/` folder.
- Never point a new `mongod` at a partially-copied data directory.
- Always keep the pre-recovery backup until you have verified the restored data.
