Release Notes
=============

v2.0.0
------

.. warning::

   This release changes two default behaviors: content blocks can no
   longer be created manually via the admin, and template scanning
   now runs automatically (and writes to the database) after
   ``migrate``/on app startup unless disabled. See below and
   :doc:`indexing`.

* Add template usage indexing: ``TinyContentIndexer.build()`` scans
  templates for ``tinycontent``/``tinycontent_simple`` tag usages,
  records them in a new ``TinyContentUsage`` model, and autocreates
  a blank content block for any referenced name that doesn't exist
  yet. Runs automatically after ``migrate`` (production) or on app
  startup (``DEBUG=True``) unless ``TINYCONTENT_AUTO_INDEX = False``,
  and can otherwise be triggered via the new ``tinycontent_index``
  management command, an admin action, or directly.
* **Backwards incompatible:** content blocks can no longer be created
  manually via the admin - only the indexer creates them now.
* ``TinyContent`` gains ``title`` (auto-derived from ``name``),
  ``active`` (an admin-facing bookkeeping flag) and ``autocreated``
  fields. ``name`` is read-only once a block exists.
* **Backwards incompatible:** content blocks that are still
  referenced by a template can no longer be deleted.
* See :doc:`indexing` and :doc:`managing_blocks` for details.

v1.0.1
------

* Added Makefile helper commands for the demo dev container
  (``demo-build``, ``demo-up``, ``demo-shell``, ``demo-down``,
  ``demo-reset``).

v1.0.0
------

* Modernization: dropped support for Django versions below 5.2 and
  Python versions below 3.10.
* Migrated packaging to ``pyproject.toml`` (``setup.py``/``setup.cfg``
  removed).
* Added type hints across the package, plus a ``py.typed`` marker.
* Switched linting from flake8 to Ruff.
* Added GitHub Actions CI, replacing Travis CI and tox.
* Replaced the legacy ``{% blocktrans %}`` template tag with its
  modern alias, ``{% blocktranslate %}``.

v0.9.0
------

* Update for recent Django versions (thanks to @ataylor32).

v0.8.0
------

* Update for recent Django versions, remove support for older
  Django/Python versions. Supported Django versions are now 2.0 to
  3.0, supported Python versions are Python 3.6, 3.7 and 3.8 (thanks
  @ad-m).

v0.7.1
------

* Added migration required for Python 3 (thanks @markus-hinsche).

v0.7.0
------

* Compatibility changes for Django 1.11 - dropped support for
  versions of Django earlier than 1.8, and Python 3.4 (Python 2.7 and
  Python 3.5 are still supported).

v0.6.1
------

* Modify cache name, to prevent warnings for non-ASCII characters or
  whitespace (thanks @ad-m).

v0.6.0
------

* Compatibility changes for Django 1.10.

v0.5.1
------

* Added a Polish translation and locale (thanks @ad-m).

v0.5.0
------

* Add support for multiple arguments to both the ``tinycontent`` and
  the ``tinycontent_simple`` template tags. See the documentation
  about :ref:`multiple-arguments`.
* Start caching database queries - fetching a TinyContent block by
  name (as the template tags do), will only hit the database the
  first time that content block is loaded (unless the content block
  is changed).

v0.4.0
------

* Require at least django-autoslug 1.8.0, to fix a warning about
  unapplied migrations.

v0.3.0
------

* Drop support for Django 1.4 (it's quite hard to support Django 1.4
  and 1.9 in a single release - since Django 1.4 requires ``{% load
  url from future %}``, and Django 1.9 doesn't support it).
* Ensure the wheel we upload to PyPI is universal.
* Forward compatibility for Django 1.9 - remove the ``{% load url
  from future %}`` from tinycontent templates.

v0.2.1
------

* Forwards compatibility change for Django 1.9 - which will remove
  the version of ``importlib`` bundled with Django. All supported
  versions of Python (2.7, 3.3 and 3.4) have ``importlib``.

v0.2.0
------

* Dropped support for Python 2.6.
* Added a built-in markdown filter - you can use it by setting
  ``TINYCONTENT_FILTER`` to
  ``'tinycontent.filters.md.markdown_filter'``.
* Added the ability to include links to files which you can upload
  via the admin.
* Added support for setting ``TINYCONTENT_FILTER`` to a list of
  dotted paths, to allow chaining filters.

v0.1.8
------

* Added the ``TINYCONTENT_FILTER`` setting for controlling the way
  content is output.
* Improved testing with Travis (we now test all supported Python
  versions and Django versions).
