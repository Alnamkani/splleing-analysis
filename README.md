# splleing-analysis

Local, lightweight system-wide keystroke capture that reconstructs words and stores them in SQLite for offline spelling analysis.

## How it works

1. A background listener captures keystrokes system-wide via macOS Accessibility API
2. Keystrokes are reconstructed into words (handling backspace, modifiers, etc.)
3. Completed words are batch-inserted into a local SQLite database
4. An analysis script queries the database to find misspellings and word frequencies

## Setup

```bash
uv sync
```

## Usage

### Capture (requires macOS Accessibility permission)

```bash
uv run python src/capture.py
```

### Analyze

```bash
uv run python src/analyze.py
```

## Privacy

- All data stays local — no network calls
- Only completed words are stored, never raw keystrokes
- SQLite database is stored at `~/.splleing-analysis/words.db` with `600` permissions

## Plan

See [docs/PLAN.md](docs/PLAN.md) for the full implementation plan and progress tracking.
