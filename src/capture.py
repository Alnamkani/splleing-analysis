import atexit
import os
import signal
import sys
import threading
from pathlib import Path

from pynput import keyboard

from src.db import WordBuffer, ensure_db


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PID_FILE = DATA_DIR / "capture.pid"
MAX_BUFFER_LEN = 100

char_buffer: list[str] = []
word_buffer: WordBuffer | None = None
flush_timer: threading.Event = threading.Event()


def flush_word() -> None:
    if not char_buffer or word_buffer is None:
        return
    word = "".join(char_buffer).strip()
    char_buffer.clear()
    if word and len(word) < MAX_BUFFER_LEN:
        word_buffer.add(word)


def on_press(key: keyboard.Key | keyboard.KeyCode) -> None:
    try:
        if hasattr(key, "char") and key.char is not None:
            if len(char_buffer) < MAX_BUFFER_LEN:
                char_buffer.append(key.char)
        elif key == keyboard.Key.space or key == keyboard.Key.enter or key == keyboard.Key.tab:
            flush_word()
        elif key == keyboard.Key.backspace:
            if char_buffer:
                char_buffer.pop()
        elif key in (keyboard.Key.cmd, keyboard.Key.cmd_r, keyboard.Key.ctrl, keyboard.Key.ctrl_r):
            char_buffer.clear()
    except AttributeError:
        pass


def periodic_flush() -> None:
    while not flush_timer.is_set():
        flush_timer.wait(5)
        if word_buffer:
            word_buffer.flush()


def shutdown(signum: int, frame) -> None:
    flush_word()
    if word_buffer:
        word_buffer.flush()
    if PID_FILE.exists():
        PID_FILE.unlink()
    sys.exit(0)


def main() -> None:
    global word_buffer

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if PID_FILE.exists():
        old_pid = PID_FILE.read_text().strip()
        try:
            os.kill(int(old_pid), 0)
            print(f"Already running (pid={old_pid}).")
            sys.exit(1)
        except (OSError, ValueError):
            PID_FILE.unlink()

    atexit.register(lambda: PID_FILE.unlink(missing_ok=True))

    PID_FILE.write_text(str(os.getpid()))

    conn = ensure_db()
    word_buffer = WordBuffer(conn)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    timer_thread = threading.Thread(target=periodic_flush, daemon=True)
    timer_thread.start()

    print("Listening for keystrokes... (Ctrl+C to stop)")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    main()
