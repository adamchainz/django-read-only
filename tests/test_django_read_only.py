from __future__ import annotations

import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import Any, Callable
from unittest import mock

import pytest
from django.contrib.sites.models import Site
from django.db import connection, transaction
from django.db.backends.utils import CursorWrapper
from django.test import SimpleTestCase, TestCase, override_settings
from psycopg.sql import SQL, Composable

import django_read_only

set_env_vars = partial(mock.patch.dict, os.environ)


@contextmanager
def patch_psycopg_composable_support_onto_cursor():
    """
    Make Django's default CursorWrapper convert psycopg's Composable objects to
    strings, to allow the test suite using SQLite to check the support for
    these objects.
    """
    orig_execute = CursorWrapper._execute  # type: ignore [attr-defined]

    def execute_wrapper(self, sql, *args, **kwargs):  # pragma: no cover
        if isinstance(sql, Composable):
            sql = sql.as_string(None)
        return orig_execute(self, sql, *args, **kwargs)

    CursorWrapper._execute = execute_wrapper  # type: ignore [attr-defined]

    try:
        yield
    finally:
        CursorWrapper._execute = orig_execute  # type: ignore [attr-defined]


class DjangoReadOnlyTests(TestCase):
    def tearDown(self):
        # reset after every test
        django_read_only.read_only = False
        super().tearDown()

    def test_set_read_only_default_false(self):
        """
        Check that, in the absence of a value for the setting and environment
        variable, AppConfig.ready() defaults read only mode to OFF.
        """
        with set_env_vars(DJANGO_READ_ONLY=""):
            django_read_only.set_read_only()

            assert not django_read_only.read_only

    def test_set_read_only_setting_on(self):
        """
        Check that if the setting is True, AppConfig.ready() defaults read only
        mode to ON.
        """
        with (
            set_env_vars(DJANGO_READ_ONLY=""),
            override_settings(DJANGO_READ_ONLY=True),
        ):
            django_read_only.set_read_only()

            assert django_read_only.read_only

    def test_set_read_only_env_var_on(self):
        """
        Check that if the environment variable is set to anything whilst the
        setting is undefined, AppConfig.ready() sets read only mode ON.
        """
        with set_env_vars(DJANGO_READ_ONLY="something"):
            django_read_only.set_read_only()

            assert django_read_only.read_only

    def test_set_read_only_setting_precedence_to_env_var(self):
        """
        Check that if both the setting and environment variable are set,
        the setting takes precedence.
        """
        with (
            set_env_vars(DJANGO_READ_ONLY="=something"),
            override_settings(DJANGO_READ_ONLY=False),
        ):
            django_read_only.set_read_only()

            assert not django_read_only.read_only

    def test_setting_changed(self):
        """
        Check that if the setting changes, read_only mode updates
        appropriately.
        """
        with override_settings(DJANGO_READ_ONLY=False):
            assert not django_read_only.read_only

            with override_settings(DJANGO_READ_ONLY=True):
                assert django_read_only.read_only

    def test_setting_changed_different_setting(self):
        """
        Check that if a different setting changes, read_only doesn't change.
        """
        with override_settings(SITE_ID=2):
            assert not django_read_only.read_only

    def test_disable_writes(self):
        django_read_only.disable_writes()

        with pytest.raises(django_read_only.DjangoReadOnlyError):
            Site.objects.create(domain="example.org", name="Example org")

    def test_disable_writes_allows_selects(self):
        django_read_only.disable_writes()

        Site.objects.count()

    def test_disable_writes_allows_space_prefix(self):
        django_read_only.disable_writes()

        with connection.cursor() as cursor:
            cursor.execute(" SELECT 1")
            row = cursor.fetchone()
        assert row == (1,)

    def test_disable_writes_allows_newline_prefix(self):
        django_read_only.disable_writes()

        with connection.cursor() as cursor:
            cursor.execute("\nSELECT 1")
            row = cursor.fetchone()
        assert row == (1,)

    def test_disable_writes_allows_union(self):
        django_read_only.disable_writes()

        Site.objects.order_by().union(Site.objects.order_by()).count()

    def test_disable_writes_allows_psycopg_sql_select(self):
        django_read_only.disable_writes()

        with (
            patch_psycopg_composable_support_onto_cursor(),
            connection.cursor() as cursor,
        ):
            cursor.execute(SQL("SELECT 1"))
            row = cursor.fetchone()
        assert row == (1,)

    def test_disable_writes_disallows_psycopg_sql_update(self):
        django_read_only.disable_writes()

        with (
            patch_psycopg_composable_support_onto_cursor(),
            pytest.raises(django_read_only.DjangoReadOnlyError),
            connection.cursor() as cursor,
        ):
            cursor.execute(SQL("UPDATE something"))

    def test_disable_writes_disallows_unsupported_types(self):
        django_read_only.disable_writes()

        with (
            pytest.raises(django_read_only.DjangoReadOnlyError),
            connection.cursor() as cursor,
        ):
            cursor.execute(123)  # type: ignore [arg-type]

    def test_disable_writes_allows_atomics_around_reads(self):
        django_read_only.disable_writes()

        with transaction.atomic():
            Site.objects.count()

    def test_enable_writes(self):
        django_read_only.enable_writes()

        Site.objects.create(domain="example.org", name="Example org")

    def test_temp_writes(self):
        django_read_only.disable_writes()

        with django_read_only.temp_writes():
            Site.objects.create(domain="example.org", name="Example org")

        with pytest.raises(django_read_only.DjangoReadOnlyError):
            Site.objects.create(domain="example.co", name="Example co")

    def test_alongside_other_instrumentation(self):
        def noop(
            execute: Callable[[str, str, bool, dict[str, Any]], Any],
            sql: Any,
            params: str,
            many: bool,
            context: dict[str, Any],
        ) -> Any:
            return execute(sql, params, many, context)

        def threadable() -> list[Any]:
            with connection.execute_wrapper(noop), connection.cursor() as cursor:
                cursor.execute("SELECT 1234")

            return connection.execute_wrappers

        with ThreadPoolExecutor(max_workers=1) as executor:
            result = executor.submit(threadable).result()

        assert result == [django_read_only.blocker]


REPO_PATH = Path(__file__).resolve().parent.parent
PYPROJECT_PATH = str(REPO_PATH / "pyproject.toml")


class IPythonTests(SimpleTestCase):
    # Depends on monkeypatching sys.stdin.isatty() in tests/__init__.py

    def run_ipython_shell(
        self, input_lines: list[str]
    ) -> subprocess.CompletedProcess[str]:
        proc = subprocess.run(
            [sys.executable, "-m", "django", "shell", "-i", "ipython"],
            input="\n".join(input_lines),
            capture_output=True,
            cwd=REPO_PATH,
            env={
                "DJANGO_SETTINGS_MODULE": "tests.settings",
                "DJANGO_READ_ONLY": "1",
                "COVERAGE_PROCESS_START": PYPROJECT_PATH,
            },
            text=True,
        )
        assert proc.returncode == 0
        return proc

    def test_load_unload(self):
        proc = self.run_ipython_shell(
            [
                r"%load_ext django_read_only",
                r"%unload_ext django_read_only",
            ]
        )

        lines = proc.stdout.splitlines()
        assert lines[-3:] == [
            "In [1]: ",
            "In [2]: ",
            "In [3]: Do you really want to exit ([y]/n)? ",
        ]
        assert proc.stderr == ""

    def test_error_message(self):
        proc = self.run_ipython_shell(
            [
                r"%load_ext django_read_only",
                "from django.db import connection",
                "connection.cursor().execute('INSERT INTO DUAL')",
            ]
        )

        lines = proc.stdout.splitlines()
        assert re.sub(r"\x1b.*?m", "", lines[-3]) == (
            "DjangoReadOnlyError: Write queries are currently disabled. "
            + "Enable with '%read_only off' or django_read_only.enable_writes()."
        )
        assert proc.stderr == ""

    def test_read_only_on(self):
        proc = self.run_ipython_shell(
            [
                r"%load_ext django_read_only",
                r"%read_only on",
            ]
        )

        lines = proc.stdout.splitlines()
        assert lines[-4:] == [
            "In [1]: ",
            "In [2]: Write queries disabled.",
            "",
            "In [3]: Do you really want to exit ([y]/n)? ",
        ]
        assert proc.stderr == ""

    def test_read_only_off(self):
        proc = self.run_ipython_shell(
            [
                r"%load_ext django_read_only",
                r"%read_only off",
            ]
        )

        lines = proc.stdout.splitlines()
        assert lines[-4:] == [
            "In [1]: ",
            "In [2]: Write queries enabled.",
            "",
            "In [3]: Do you really want to exit ([y]/n)? ",
        ]
        assert proc.stderr == ""

    def test_read_only_unknown(self):
        proc = self.run_ipython_shell(
            [
                r"%load_ext django_read_only",
                r"%read_only whatever",
            ]
        )

        lines = proc.stdout.splitlines()
        assert lines[-4:] == [
            "In [1]: ",
            "In [2]: Unknown value 'whatever', pass 'on' or 'off'.",
            "",
            "In [3]: Do you really want to exit ([y]/n)? ",
        ]
        assert proc.stderr == ""
