#!/usr/bin/env python3
"""Keep compiler failures visible without flooding BuildKit's step log."""
import os
from pathlib import Path
import re
import subprocess
import sys


def run_build(command, log):
    # A deploy host also runs MySQL and the application. Do not allocate one
    # compiler for every CPU reported by the host/container.
    workers = min(2, len(os.sched_getaffinity(0)))
    env = dict(os.environ, DEB_BUILD_OPTIONS=f"parallel={workers}")
    print(f"OpenSSL: building Debian packages and running regression tests; jobs={workers}", flush=True)
    with log.open("w") as output:
        process = subprocess.Popen(command, env=env, stdout=output, stderr=subprocess.STDOUT)
        while True:
            try:
                status = process.wait(timeout=30)
                break
            except subprocess.TimeoutExpired:
                print(f"OpenSSL: build still running; captured {log.stat().st_size} bytes", flush=True)
    status = status if status >= 0 else 128 - status
    if not status:
        print("PASS OpenSSL: package build and upstream regression tests completed", flush=True)
        return 0

    print(f"OpenSSL BUILD FAILED: exit={status}; diagnostic excerpts follow", flush=True)
    # The first compiler failure may be far before the tail when parallel jobs
    # finish normally afterwards. Keep both early/late errors and the final tail.
    pattern = re.compile(
        r"fatal error|error:|\berror \d|undefined reference|\bkilled\b|"
        r"cannot allocate|no space left|not ok|result: fail|failed tests|"
        r"unmet build dep|cannot find|no rule to make|segmentation fault",
        re.IGNORECASE,
    )
    # Read twice so the captured log can grow large without retaining it in RAM.
    first, last, count = [], [], 0
    first_diagnostic = None
    with log.open(errors="replace") as output:
        for count, line in enumerate(output, 1):
            if pattern.search(line):
                if first_diagnostic is None:
                    first_diagnostic = line.rstrip()[:1000]
                if len(first) < 6:
                    first.append(count)
                last = (last + [count])[-6:]
    selected = set(range(max(1, count - 59), count + 1))
    for number in first + last:
        selected.update(range(max(1, number - 2), number + 3))
    with log.open(errors="replace") as output:
        for number, line in enumerate(output, 1):
            if number in selected:
                print(f"{number}: {line.rstrip()[:1000]}", flush=True)
    # BuildKit repeats only a short tail in its final error summary.
    if first_diagnostic is not None:
        print(f"OpenSSL first diagnostic: {first_diagnostic}", flush=True)
    print(f"OpenSSL BUILD FAILED: exit={status}", flush=True)
    return status


if __name__ == "__main__":
    sys.exit(run_build(
        ["dpkg-buildpackage", "-B", "-us", "-uc", "-Pnoudeb"],
        Path("/tmp/openssl-build.log"),
    ))
