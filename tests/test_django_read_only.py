import os
from unittest import mock

import pytest
from django.contrib.sites.models import Site
from django.db import transaction
from django.test import TestCase

import django_read_only


class DjangoReadOnlyTests(TestCase):
    def test_ready_default_false(self):
        """
        Check that, in the absence of a value for DJANGO_READ_ONLY,
        AppConfig.ready() defaults read only mode to OFF.
        """
        with mock.patch.dict(os.environ, {"DJANGO_READ_ONLY": ""}):
            django_read_only.DjangoReadOnlyAppConfig("name", django_read_only).ready()

        assert not django_read_only.read_only

    def test_ready_env_var_set(self):
        """
        Check that if DJANGO_READ_ONLY is set to anything, the
        AppConfig.ready() sets read only mode ON.
        """
        with mock.patch.dict(os.environ, {"DJANGO_READ_ONLY": "something"}):
            django_read_only.DjangoReadOnlyAppConfig("name", django_read_only).ready()

        assert django_read_only.read_only

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
