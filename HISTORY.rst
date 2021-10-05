=======
History
=======

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
