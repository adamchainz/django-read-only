django-read-only
================

.. image:: https://github.com/adamchainz/django-read-only/workflows/CI/badge.svg?branch=master
   :target: https://github.com/adamchainz/django-read-only/actions?workflow=CI

.. image:: https://img.shields.io/pypi/v/django-read-only.svg
   :target: https://pypi.org/project/django-read-only/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/python/black

Disable Django database writes.

Requirements
------------

Python 3.5 to 3.8 supported.

Django 2.2 to 3.0 supported.

----

**Deploying a Django project?**
**Testing a Django project?**
**Are your tests slow?**
Check out my book `Speed Up Your Django Tests <https://gumroad.com/l/suydt>`__ which covers loads of best practices so you can write faster, more accurate tests.

----

Installation
------------

Install with **pip**:

.. code-block:: sh

    python -m pip install django-read-only

Then add to your installed apps:

.. code-block:: python

    INSTALLED_APPS = [
        ...,
        "django_read_only",
        ...
    ]

Usage
-----

Set the environment variable ``DJANGO_READ_ONLY`` to anything but the empty string, and all data modification queries will cause an exception:

.. code-block:: sh

    DJANGO_READ_ONLY=1 python manage.py shell
    ...
    >>> User.objects.create_user(username="hacker", password="hunter2")
    ...
    DjangoReadOnlyError(...)

You can put this in the shell profile file (``bashrc``, ``zshrc``, etc.) of the user on your production system.
This way developers performing exploratory queries can’t accidentally make changes, but writes remain enabled for non-shell processes like your WSGI server.

During a session with ``DJANGO_READ_ONLY`` set, you can re-enable writes for the current thread by calling ``enable_writes()``:

.. code-block:: pycon

    >>> import django_read_only
    >>> django_read_only.enable_writes()

Writes can be disabled with ``disable_writes()``:

.. code-block:: pycon

    >>> django_read_only.disable_writes()

To temporarily allow writes, use the ``temp_writes()`` context manager / decorator:

.. code-block:: pycon

    >>> with django_read_only.temp_writes():
    ...      User.objects.create_user(...)
