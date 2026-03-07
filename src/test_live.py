import sys

from pynput import keyboard


MAX_BUFFER_LEN = 100
char_buffer: list[str] = []


def flush_word() -> None:
    if not char_buffer:
        return
    word = "".join(char_buffer).strip()
    char_buffer.clear()
    if word:
        print(f"  WORD: {word}")


def on_press(key: keyboard.Key | keyboard.KeyCode) -> None:
    try:
        if hasattr(key, "char") and key.char is not None:
            if len(char_buffer) < MAX_BUFFER_LEN:
                char_buffer.append(key.char)
            print(f"  char: {key.char!r}  buffer: {''.join(char_buffer)}")
        elif key == keyboard.Key.space or key == keyboard.Key.enter or key == keyboard.Key.tab:
            print(f"  [{key.name}]")
            flush_word()
        elif key == keyboard.Key.backspace:
            if char_buffer:
                char_buffer.pop()
            print(f"  [backspace]  buffer: {''.join(char_buffer)}")
        elif key in (keyboard.Key.cmd, keyboard.Key.cmd_r, keyboard.Key.ctrl, keyboard.Key.ctrl_r):
            char_buffer.clear()
            print(f"  [{key.name}] buffer cleared")
        else:
            print(f"  [ignored: {key}]")
    except AttributeError:
        pass


def main() -> None:
    print("Live keystroke test — type anywhere, see output here.")
    print("Press Ctrl+C to stop.\n")
    try:
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    except KeyboardInterrupt:
        flush_word()
        print("\nStopped.")


if __name__ == "__main__":
    main()
