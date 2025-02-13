=========
Changelog
=========

1.19.0 (2025-02-06)
-------------------

* Support Django 5.2.

1.18.0 (2024-10-29)
-------------------

* Drop Django 3.2 to 4.1 support.

1.17.0 (2024-10-20)
-------------------

* Add support for inspecting SQL using `psycopg 3’s SQL API <https://www.psycopg.org/psycopg3/docs/api/sql.html>`__.

* Drop Python 3.8 support.

* Support Python 3.13.

1.16.0 (2024-06-19)
-------------------

* Support Django 5.1.

1.15.0 (2023-10-11)
-------------------

* Support Django 5.0.

1.14.0 (2023-07-10)
-------------------

* Drop Python 3.7 support.

1.13.0 (2023-06-14)
-------------------

* Support Python 3.12.

1.12.0 (2023-02-25)
-------------------

* Support Django 4.2.

1.11.0 (2022-10-05)
-------------------

* Add IPython extension, allowing you to use line magic to change read-only mode with less typing:

  .. code-block:: ipython

      In [1]: %read_only off
      Write queries enabled.

1.10.1 (2022-10-03)
-------------------

* Fix a bug where threads creating connections with ``execute_wrapper()`` would incorrectly have django-read-only’s instrumentation removed on exit of ``execute_wrapper()``, instead of their own.

  Thanks to Christian Bundy for the report in `Issue #180 <https://github.com/adamchainz/django-read-only/issues/180>`__.

1.10.0 (2022-07-20)
-------------------

* Allow read-only-looking queries that start with space, newline, or “(”.
  The later allows ``QuerySet.union()`` and related methods to work.

  Thanks to Kevin Marsh for the report in `Issue #166 <https://github.com/adamchainz/django-read-only/issues/166>`__.

1.9.0 (2022-06-05)
------------------

* Support Python 3.11.

* Support Django 4.1.

1.8.0 (2022-05-10)
------------------

* Drop support for Django 2.2, 3.0, and 3.1.

1.7.0 (2022-01-10)
------------------

* Drop Python 3.6 support.

1.6.0 (2021-10-05)
------------------

* Support Python 3.10.

1.5.0 (2021-09-28)
------------------

* Support Django 4.0.

1.4.0 (2021-08-14)
------------------

* Add type hints.

* Stop distributing tests to reduce package size. Tests are not intended to be
  run outside of the tox setup in the repository. Repackagers can use GitHub's
  tarballs per tag.

1.3.0 (2021-01-25)
------------------

* Support Django 3.2.

1.2.0 (2020-12-16)
------------------

* Drop Python 3.5 support.

1.1.2 (2020-11-25)
------------------

* Allow ``EXPLAIN`` queries.

1.1.1 (2020-11-18)
------------------

* Support Python 3.9.
* Add a hint on how to enable writes in the ``DjangoReadOnlyError`` message.

1.1.0 (2020-10-08)
------------------

* Add support for a ``DJANGO_READ_ONLY`` setting, to allow finer grained
  customization of when read-only mode is enabled.

1.0.0 (2020-10-01)
------------------

* Initial release.
