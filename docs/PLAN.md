# Splleing Analysis — Implementation Plan

Local, lightweight system-wide keystroke capture that reconstructs words and stores them in SQLite for offline spelling analysis.

## Architecture

Single Python process using `pynput` for macOS Accessibility API keystroke capture. Event-driven (no polling). All data stays local in SQLite.

**Data pipeline:** `keystroke events → character buffer → word (on space/enter) → SQLite`

## Components & Status

### 1. Global Keyboard Listener — `src/capture.py`
- [ ] `pynput` keyboard listener (event-driven, low CPU)
- [ ] Filter out modifier keys, function keys, media keys
- [ ] Ignore modifier combos (Cmd+X, Ctrl+C) — clear buffer on Cmd
- [ ] Graceful shutdown on SIGINT/SIGTERM — flush buffer before exit
- [ ] PID file at `~/.splleing-analysis/capture.pid` to prevent duplicates

### 2. Word Reconstruction Engine — `src/capture.py`
- [ ] In-memory character buffer (list of chars, capped at 100)
- [ ] Space / Return / Tab → flush buffer as completed word
- [ ] Backspace → pop last char
- [ ] Non-printable keys → skip
- [ ] Discard words that look like password input (heuristic)

### 3. SQLite Storage — `src/db.py`
- [ ] DB file: `~/.splleing-analysis/words.db`
- [ ] Schema: `words(id INTEGER PRIMARY KEY, word TEXT, timestamp TEXT)`
- [ ] WAL mode for performance
- [ ] Batch insert: flush every ~10 words or every 5 seconds
- [ ] File permissions: `chmod 600`

### 4. Analysis Script — `src/analyze.py`
- [ ] Query SQLite for word frequencies
- [ ] Flag misspellings using `difflib` against a word list
- [ ] Output: top misspelled words, frequency, suggestions
- [ ] CLI interface for filtering by date range

### 5. Daemon Management
- [ ] Start/stop commands via CLI entry point
- [ ] Optional `launchd` plist for auto-start on macOS
- [ ] Logging to `~/.splleing-analysis/capture.log`

## Performance Targets

| Metric | Target |
|--------|--------|
| RAM | < 15 MB |
| CPU | Near zero (event-driven) |
| Disk I/O | Batched writes, negligible |
| Dependencies | `pynput` only |

## Privacy Safeguards

- Only completed words stored, never raw keystrokes
- No network calls
- SQLite file is local, user-owned, `chmod 600`
- Password heuristic: discard abnormally long buffers without spaces

## File Structure

```
splleing-analysis/
├── src/
│   ├── capture.py      # Keyboard listener + word reconstruction
│   ├── db.py           # SQLite operations
│   └── analyze.py      # Offline spelling analysis
├── docs/
│   └── PLAN.md         # This file
├── pyproject.toml
└── README.md
```

## Prerequisites

- macOS Accessibility permission granted to the terminal running the script
- Python 3.11+
- `uv` for dependency management
