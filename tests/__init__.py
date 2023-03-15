from __future__ import annotations

import sys

import coverage

coverage.process_startup()


# Patch for IPythonTests
# Fool Django’s shell command into thinking we’re a TTY, so that it continues
# to open IPython
if not sys.stdin.isatty():  # pragma: no cover

    def fake_isatty(*args, **kwargs):
        return True

    sys.stdin.isatty = fake_isatty  # type: ignore [method-assign]
