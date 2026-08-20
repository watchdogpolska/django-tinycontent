.. _indexing:

Template Usage Indexing
========================

django-tinycontent can scan your project's templates for
``tinycontent``/``tinycontent_simple`` tag usages, so you don't have
to hunt for content blocks by clicking through pages. Running the
indexer:

* Records every template path and line number where each content
  block is referenced (``TinyContentUsage``, visible read-only on
  each block's admin page).
* Autocreates a blank, inactive content block for any referenced name
  that doesn't exist yet.
* Marks blocks it created itself as inactive again if a later scan no
  longer finds any reference to them (blocks you didn't create
  yourself are never touched this way).

.. contents::
   :local:

Only tag calls with a literal, quoted name (e.g. ``{% tinycontent
'welcome' %}``) can be discovered by the scanner. Calls that build the
name from a template variable (e.g. ``{% tinycontent page.slug %}``)
are skipped, since their value can't be known without rendering the
page - these are reported as warnings wherever the index is built.

Running the Indexer
--------------------

The indexing logic lives in a single place,
``TinyContentIndexer.build()``, so every trigger below behaves
identically. Pick whichever fits your deployment:

Management command
^^^^^^^^^^^^^^^^^^^

::

    python manage.py tinycontent_index

Admin action
^^^^^^^^^^^^

Select any row in the ``TinyContent`` admin list and choose "Rebuild
template usage index" from the actions dropdown - the selection
itself is ignored, the whole project is always rescanned.

Programmatically
^^^^^^^^^^^^^^^^^

Call the indexer directly from a deployment hook, Celery task, or
anywhere else::

    from tinycontent.indexer import TinyContentIndexer

    TinyContentIndexer.build()

Automatic Indexing
-------------------

To avoid scanning templates on every request, the indexer is never
triggered by a page view. Instead it's automatically triggered:

* After ``manage.py migrate`` completes, when ``DEBUG`` is ``False``.
* When the app registry is ready, when ``DEBUG`` is ``True`` (e.g. on
  ``manage.py runserver`` startup).

Both of these can be disabled with:

::

    TINYCONTENT_AUTO_INDEX = False

(automatic indexing is also always skipped while running under
pytest, to avoid surprise content blocks being created by test runs).
