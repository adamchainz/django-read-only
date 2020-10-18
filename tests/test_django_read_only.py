import os
from functools import partial
from unittest import mock

import pytest
from django.contrib.sites.models import Site
from django.db import transaction
from django.test import TestCase, override_settings

import django_read_only

set_env_vars = partial(mock.patch.dict, os.environ)


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
        with set_env_vars(DJANGO_READ_ONLY=""), override_settings(
            DJANGO_READ_ONLY=True
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
        the setting takes precendence.
        """
        with set_env_vars(DJANGO_READ_ONLY="=something"), override_settings(
            DJANGO_READ_ONLY=False
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
