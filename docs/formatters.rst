.. _RST grid tables: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#tables
.. _Rich: https://rich.readthedocs.io/

.. _formatters_intro:

=======
Formats
=======

.. _formatters_rst:

RestructuredText
****************

This is the default format used from commands.

It will output analyze and possibles failures in differents `RST grid tables`_ that you
can include in your RST documents.

Example
-------

.. include:: ../tests/data_fixtures/formatted/with_failures.rst
    :code: text


Rich
****

It will output analyze and possibles failures with `Rich`_ library.

This is an optional format if you installed Dependency-comb with the ``rich`` feature,
see :ref:`install_intro` document. If ``rich`` is not listed in available formats in
commands then you didn't installed Rich.

.. Note::
    The example will look better in a terminal than on this HTML page where characters
    don't display well and example has been saved without terminal colors.

Example
-------

.. include:: ../tests/data_fixtures/formatted/with_failures.rich
    :code: text


JSON
****

It will output analyze and possibles failures in a JSON structure.

Example
-------

.. include:: ../tests/data_fixtures/formatted/with_failures.json
    :code: text

