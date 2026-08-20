Adding and Editing Blocks
-------------------------

Content blocks are created automatically by the :doc:`template usage
indexer <indexing>` the first time it finds a ``tinycontent`` or
``tinycontent_simple`` tag referencing a name that doesn't exist yet -
there's no "Add" button in the admin. Once a block exists, it's edited
using Django's admin interface.

Each content block has:

* ``name`` - the identifier used in templates. Read-only once the
  block has been created.
* ``title`` - a human-readable label, auto-filled from ``name`` the
  first time the block is saved (replacing ``:-_.`` with spaces and
  capitalizing each word), but editable afterwards.
* ``content`` - the raw content, rendered through any configured
  :ref:`filters`. Edited as a plain textarea by default, or with a
  `TinyMCE <https://github.com/jazzband/django-tinymce>`_ rich text
  editor - see :doc:`installation`.
* ``active`` - an admin-facing bookkeeping flag. It does not affect
  rendering.
* A read-only list of every template/line where the block is
  referenced, rebuilt each time the indexer runs.

If a block with the name given in the template tag cannot be found,
or exists but has no content yet, either nothing is rendered (if using
``tinycontent_simple``), or the text between ``tinycontent`` and
``endtinycontent`` is rendered (if using the more complex variant).

If you're logged in as a user with permission to edit content blocks
(which you can set via permissions in the Django admin), and the
block already exists but has no content, you'll see a link to edit it
directly.

Content blocks that no longer have any recorded template usage can be
deleted from the admin; blocks that are still referenced somewhere
can't be deleted until that reference is removed and the index is
rebuilt.
