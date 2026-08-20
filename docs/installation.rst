Installation
------------

Installation is simple::

    pip install django-tinycontent

Then, add ``tinycontent`` to your ``INSTALLED_APPS``.

TinyMCE admin editor (optional)
--------------------------------

By default, ``content`` is edited in the admin as a plain textarea. You
can switch it to a `django-tinymce`_ rich text editor instead::

    pip install "django-tinycontent[tinymce]"

Then add ``tinymce`` to ``INSTALLED_APPS`` (alongside ``tinycontent``)
and set::

    TINYCONTENT_USE_TINYMCE = True

``django-tinymce`` is *not* a hard dependency of ``django-tinycontent``
— it's an optional extra with an unpinned lower bound
(``django-tinymce>=5``), and it's only imported when
``TINYCONTENT_USE_TINYMCE`` is enabled. That means installing
``django-tinycontent`` never forces a ``django-tinymce`` version on your
project: if your project already depends on ``django-tinymce`` for its
own models, pip resolves to a single shared install that satisfies both
constraints, rather than two conflicting pins. If you enable the
setting without the package installed, you'll get a clear
``ImproperlyConfigured`` error rather than a silent failure.

The widget defaults ``license_key`` to ``"gpl"`` (TinyMCE 6+ requires
this to be set to avoid the "evaluation mode" nag, and this package
only ships the fully self-hosted, GPL-licensed static assets, not a
Tiny Cloud integration) unless your own ``TINYMCE_DEFAULT_CONFIG``
already sets a ``license_key``, in which case yours is respected as-is.

.. _django-tinymce: https://github.com/jazzband/django-tinymce

Version Support
---------------

Python 3.10, 3.11, 3.12 and 3.13 are supported, along with Django
5.2 and above.
