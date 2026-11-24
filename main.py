"""The Long Roast: one line roasting the AI agent this runs on.

Writes exactly one line of at most 200 characters to entry.txt.
Pure Python standard library only.
"""

import os
import stat
import tempfile

MAX_CHARS = 200

LINE = (
    "My agent never says 'I don't know': it apologizes, writes a "
    "40-line plan, fixes the wrong file, and calls it 'iterating'."
)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")

    line = LINE
    if not 1 <= len(line) <= MAX_CHARS:
        raise ValueError("line must be 1..%d chars, got %d" % (MAX_CHARS, len(line)))
    if line != line.strip() or "\n" in line or "\r" in line:
        raise ValueError("line must be a single line with no edge whitespace")

    data = line.encode("utf-8")
    fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    os.chmod(target, 0o644)

    # Read back and verify: exact bytes, no trailing newline, mode 0644.
    with open(target, "rb") as f:
        back = f.read()
    if back != data:
        raise ValueError("read-back bytes differ from written bytes")
    if back.endswith(b"\n"):
        raise ValueError("output must not end with a newline")
    mode = stat.S_IMODE(os.stat(target).st_mode)
    if mode != 0o644:
        raise ValueError("output mode must be 0644, got %o" % mode)


if __name__ == "__main__":
    main()
