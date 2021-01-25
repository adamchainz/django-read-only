================
django-read-only
================

.. image:: https://img.shields.io/github/workflow/status/adamchainz/django-read-only/CI/master?style=for-the-badge
   :target: https://github.com/adamchainz/django-read-only/actions?workflow=CI

.. image:: https://img.shields.io/coveralls/github/adamchainz/django-read-only/master?style=for-the-badge
  :target: https://app.codecov.io/gh/adamchainz/django-read-only

.. image:: https://img.shields.io/pypi/v/django-read-only.svg?style=for-the-badge
   :target: https://pypi.org/project/django-read-only/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

Disable Django database writes.

Requirements
------------

Python 3.6 to 3.9 supported.

Django 2.2 to 3.2 supported.

----

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

In your settings file, set ``DJANGO_READ_ONLY`` to ``True`` and all data modification queries will cause an exception:

.. code-block:: console

    $ DJANGO_READ_ONLY=1 python manage.py shell
    ...
    >>> User.objects.create_user(username="hacker", password="hunter2")
    ...
    DjangoReadOnlyError(...)

For convenience, you can also control this with the ``DJANGO_READ_ONLY`` environment variable, which will count as ``True`` if set to anything but the empty string.
The setting takes precedence over the environment variable.

During a session with ``DJANGO_READ_ONLY`` set on, you can re-enable writes by calling ``enable_writes()``:

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

Note that writes being enabled/disabled is global state, affecting all threads and asynchronous coroutines.

Recommended Setup
-----------------

Set read-only mode on in your production environment, and maybe staging, during interactive sessions.
This can be done by setting the ``DJANGO_READ_ONLY`` environment variable in the shell profile file (``bashrc``, ``zshrc``, etc.) of the system’s user account.
This way developers performing exploratory queries can’t accidentally make changes, but writes will remain enabled for non-shell processes like your WSGI server.

With this setup, developers can also run management commands with writes enabled by setting the environment variable before the command:

.. code-block:: console

    $ DJANGO_READ_ONLY= python manage.py clearsessions

Some deployment platforms don’t allow you to customize your shell profile files.
In this case, you will need to find a way to detect shell mode from within your settings file.

For example, on Heroku there’s the ``DYNO`` environment variable (`docs <https://devcenter.heroku.com/articles/dynos#local-environment-variables>`__) to identify the current virtual machine.
It starts with “run.” for interactive sessions.
You can use this to enable read-only mode in your settings file like so:

.. code-block:: python

    if os.environ.get("DYNO", "").startswith("run."):
        DJANGO_READ_ONLY = bool(os.environ.get("DJANGO_READ_ONLY", "1"))
    else:
        DJANGO_READ_ONLY = False

How it Works
------------

The most accurate way to prevent writes is to connect as a separate database user with only read permission.
However, this has limitations - Django doesn’t support modifying the ``DATABASES`` setting live, so sessions would not be able to temporarily allow writes.

Instead, django-read-only uses `always installed database instrumentation <https://adamj.eu/tech/2020/07/23/how-to-make-always-installed-django-database-instrumentation/>`__ to inspect executed queries and only allow those which look like reads.
It uses a “fail closed” philosophy, so anything unknown will fail, which should be fairly reasonable.

Because django-read-only uses Django database instrumentation, it cannot block queries running through the underlying database connection (accesses through ``django.db.connection.connection``), and it cannot filter operations within stored procedures (which use ``connection.callproc()``).
These are very rare in practice though, so django-read-only’s method works well for most projects.
