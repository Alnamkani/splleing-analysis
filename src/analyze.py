import sqlite3
import sys
from collections import Counter
from difflib import get_close_matches
from pathlib import Path


DB_PATH = Path.home() / ".splleing-analysis" / "words.db"
WORDS_FILE = Path("/usr/share/dict/words")


def load_dictionary() -> set[str]:
    if not WORDS_FILE.exists():
        print(f"Warning: dictionary not found at {WORDS_FILE}")
        return set()
    return {line.strip().lower() for line in WORDS_FILE.read_text().splitlines() if line.strip()}


def get_words(date_from: str | None = None, date_to: str | None = None) -> list[str]:
    if not DB_PATH.exists():
        print("No data yet. Run capture first.")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    query = "SELECT word FROM words"
    params: list[str] = []
    conditions: list[str] = []

    if date_from:
        conditions.append("timestamp >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("timestamp <= ?")
        params.append(date_to)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [row[0] for row in rows]


def analyze(date_from: str | None = None, date_to: str | None = None) -> None:
    words = get_words(date_from, date_to)
    if not words:
        print("No words captured yet.")
        return

    dictionary = load_dictionary()
    freq = Counter(w.lower() for w in words)

    print(f"\nTotal words captured: {len(words)}")
    print(f"Unique words: {len(freq)}")

    print("\n--- Top 20 Most Frequent Words ---")
    for word, count in freq.most_common(20):
        print(f"  {word:30s} {count}")

    if dictionary:
        misspelled = {w: c for w, c in freq.items() if w.isalpha() and len(w) > 1 and w not in dictionary}
        if misspelled:
            print(f"\n--- Potential Misspellings ({len(misspelled)} found) ---")
            for word, count in sorted(misspelled.items(), key=lambda x: -x[1])[:30]:
                suggestions = get_close_matches(word, dictionary, n=3, cutoff=0.8)
                suggestion_str = ", ".join(suggestions) if suggestions else "no suggestions"
                print(f"  {word:30s} (x{count}) -> {suggestion_str}")


if __name__ == "__main__":
    from_date = sys.argv[1] if len(sys.argv) > 1 else None
    to_date = sys.argv[2] if len(sys.argv) > 2 else None
    analyze(from_date, to_date)
