#!/usr/bin/env python3
"""Tests for the osc52 binary. Usage: python3 tests/test_osc52.py ./osc52

Uses only the standard library so it runs anywhere the binary does.
"""

import base64
import fcntl
import os
import random
import select
import subprocess
import sys
import tempfile
import termios

EXE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "./osc52")

failures = []


def check(name, actual, expected):
    if actual == expected:
        print("ok   -", name)
    else:
        print("FAIL -", name)
        print("       expected:", repr(expected)[:200])
        print("       actual:  ", repr(actual)[:200])
        failures.append(name)


def sequence(data):
    """The OSC 52 sequence the tool is expected to produce for `data`."""
    return b"\x1b]52;c;" + base64.b64encode(data) + b"\x07"


def run_detached(data):
    """Run osc52 with no controlling terminal, so it must fall back to stderr."""
    return subprocess.run(
        [EXE], input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True,
    )


def run_on_tty(data):
    """Run osc52 with a pty as its controlling terminal, with stdin from a pipe
    and stdout/stderr redirected to files. Returns (pty output, stdout, stderr).
    """
    master, slave = os.openpty()
    stdin_r, stdin_w = os.pipe()
    os.write(stdin_w, data)
    os.close(stdin_w)
    out_file = tempfile.TemporaryFile()
    err_file = tempfile.TemporaryFile()

    pid = os.fork()
    if pid == 0:  # child
        os.setsid()
        tty = os.open(os.ttyname(slave), os.O_RDWR)  # Linux: this claims the tty
        try:
            fcntl.ioctl(tty, termios.TIOCSCTTY, 0)  # macOS needs it spelled out
        except (AttributeError, OSError):
            pass
        os.close(tty)
        os.dup2(stdin_r, 0)
        os.dup2(out_file.fileno(), 1)
        os.dup2(err_file.fileno(), 2)
        os.execv(EXE, [EXE])
        os._exit(127)

    # The parent holds `slave` open, so reading the master never hangs up;
    # instead we read until the sequence terminator arrives.
    os.close(stdin_r)
    output = b""
    while b"\x07" not in output:
        if not select.select([master], [], [], 10)[0]:
            break  # timed out
        output += os.read(master, 4096)
    os.waitpid(pid, 0)
    os.close(master)
    os.close(slave)
    out_file.seek(0)
    err_file.seek(0)
    return output, out_file.read(), err_file.read()


# Encoding, including every base64 padding case and every byte value.
for data in [b"", b"h", b"hi", b"hey", b"hello", b"hello, world", bytes(range(256))]:
    result = run_detached(data)
    check("encodes %r" % data[:20], result.stderr, sequence(data))

random.seed(52)
for size in [1, 2, 3, 4, 5, 100, 4095, 4096, 4097]:
    data = bytes(random.getrandbits(8) for _ in range(size))
    check("encodes %d random bytes" % size, run_detached(data).stderr, sequence(data))

# A payload far larger than the internal buffers, to exercise partial writes.
big = os.urandom(4 << 20)
check("encodes 4 MiB", run_detached(big).stderr, sequence(big))

# Output goes to the terminal, never to stdout.
result = run_detached(b"hello")
check("stdout stays empty", result.stdout, b"")
check("exits successfully", result.returncode, 0)
tty_out, tty_stdout, tty_stderr = run_on_tty(b"hello")
check("writes to the controlling terminal", tty_out, sequence(b"hello"))
check("leaves stdout alone when a terminal is available", tty_stdout, b"")
check("leaves stderr alone when a terminal is available", tty_stderr, b"")

print()
if failures:
    print("%d test(s) failed" % len(failures))
    sys.exit(1)
print("all tests passed")
