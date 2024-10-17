.. _Pypi API: https://warehouse.pypa.io/api-reference/index.html

.. _overview_intro:

========
Overview
========

How it works
************

The full process of a report with command ``report`` is:

#. Parse given requirements;
#. Store each requirement as a ``PackageRequirement`` object;
#. Request API to get package informations and fill them in package object;
#. Compute package informations to build an analyze;
#. Format an analyze;

Requirement parsing is done with `packaging library <https://packaging.pypa.io/>`_
which follows `PEP 425 <https://peps.python.org/pep-0425/>`_.

Concretely, a requirement file from Pip will just work except for some
`Unsupported requirement specifiers`_.

API
***

Dependency comb use the `Pypi API`_ to get packages informations.

However commands have a ``--cachedir`` argument to store these informations and avoid
performing the same requests on consecutive command executions. This is useful if you
are debugging your project requirements but be aware that there is no way to manage
cache persistence life except removing the cache files.


Recursive included requirements
*******************************

A requirement file can include other requirement files using the Pip option ``-r ...``,
this is supported from analyzer. However remember that relative requirement file paths
are resolved from the main requirement file path or from your current position path if
you given requirements from standard input.


Unsupported requirement specifiers
**********************************

.. Hint::
    You can see every failures and warning with the ``report`` command with options
    for maximum verbosity level and enable failures inclusion.

    The command ``analyze`` can do it also but not when used to output JSON to the
    standard output.

Direct requirement URL
    Because we cannot determine the package name to get its info from pypi. Requirement
    will be assumed as a failure.

Local package path
    As the same reason than direct requirement URL. Requirement will be
    assumed as a failure.

Pip requirement option
    No requirement option are supported except ``-r``. Requirement will be
    assumed as a failure.

Invalid version
    A version specifier must be valid with
    `packaging library <https://packaging.pypa.io/>`_. If requirement specified version
    is valid but have old versions with invalid version format, these version will be
    ignored. If requirement specified version is invalid it will be assumed as a
    failure.

Invalid syntax
    Requirement that is not valid with Pip requirement definition format. Requirement
    will be assumed as a failure.


Demonstration
*************

It is assumed we have a file ``librariesio-key.txt`` at current position and that
contains a valid API key.

And with the following requirements file ``base_requirements.txt``: ::

    # Sample of valid PIP requirements syntax
    django>=1.11,<1.12
    Pillow>=3.1.1
    djangorestframework

    django-admin-shortcuts==1.2.6

    requests [security] >= 2.8.1, == 2.8.* ; python_version < "2.7"
    urllib3 @ https://github.com/urllib3/urllib3/archive/refs/tags/1.26.8.zip

    # It is possible to refer to specific local distribution paths.
    ./downloads/numpy-1.9.2-cp34-none-win32.whl

    # It is possible to refer to URLs.
    http://wxpython.org/Phoenix/snapshot-builds/wxPython_Phoenix-3.0.3.dev1820+49a8884-cp34-none-win_amd64.whl

We can build a report like this: ::

    dependency_comb -v 0 report --failures base_requirements.txt

This will print the following output: ::

    Analyzed
    ********
    +-----+------------------------+------------+------------------------------+-----------------------+
    | #   | Name                   |  Lateness  |                     Required |        Latest release |
    +=====+========================+============+==============================+=======================+
    | 1   | django                 |    178     |         1.11.9 - 6 years ago |  5.1a1 - 2 months ago |
    +-----+------------------------+------------+------------------------------+-----------------------+
    | 2   | Pillow                 |     6      | 9.5.0 - 1 year, 3 months ago |  10.4.0 - 24 days ago |
    +-----+------------------------+------------+------------------------------+-----------------------+
    | 3   | djangorestframework    |     -      |                       Latest |  3.15.2 - A month ago |
    +-----+------------------------+------------+------------------------------+-----------------------+
    | 4   | django-admin-shortcuts |     4      |          1.2.6 - 9 years ago | 2.1.1 - 10 months ago |
    +-----+------------------------+------------+------------------------------+-----------------------+
    | 5   | requests               |     56     |          2.8.1 - 8 years ago |  2.32.3 - A month ago |
    +-----+------------------------+------------+------------------------------+-----------------------+
    | 6   | urllib3                |     -      |                       Latest | 1.26.19 - A month ago |
    +-----+------------------------+------------+------------------------------+-----------------------+

    Failures
    ********
    +-----+------------------------------------------+-----------------------+-------------------------------------+
    | #   | Source                                   |        Status         | Resume                              |
    +=====+==========================================+=======================+=====================================+
    | 1   | ./downloads/numpy-1.9.2-cp34-none-       | unsupported-localpath | Local package is not supported      |
    |     | win32.whl                                |                       |                                     |
    +-----+------------------------------------------+-----------------------+-------------------------------------+
    | 2   | http://wxpython.org/Phoenix/snapshot-bui |    unsupported-url    | Direct package URL is not supported |
    |     | lds/wxPython_Phoenix-                    |                       |                                     |
    +-----+------------------------------------------+-----------------------+-------------------------------------+

.. Note::
    The timedelta here have been computed after an analyze done 25 July 2024.

Also you will have a lots of logging messages about processing, you may mute it with
a command option see :ref:`cli_logging`.

The following sections are the included RestructuredText output sample from before.

Analyzed
********
+-----+------------------------+------------+------------------------------+-----------------------+
| #   | Name                   |  Lateness  |                     Required |        Latest release |
+=====+========================+============+==============================+=======================+
| 1   | django                 |    178     |         1.11.9 - 6 years ago |  5.1a1 - 2 months ago |
+-----+------------------------+------------+------------------------------+-----------------------+
| 2   | Pillow                 |     6      | 9.5.0 - 1 year, 3 months ago |  10.4.0 - 24 days ago |
+-----+------------------------+------------+------------------------------+-----------------------+
| 3   | djangorestframework    |     -      |                       Latest |  3.15.2 - A month ago |
+-----+------------------------+------------+------------------------------+-----------------------+
| 4   | django-admin-shortcuts |     4      |          1.2.6 - 9 years ago | 2.1.1 - 10 months ago |
+-----+------------------------+------------+------------------------------+-----------------------+
| 5   | requests               |     56     |          2.8.1 - 8 years ago |  2.32.3 - A month ago |
+-----+------------------------+------------+------------------------------+-----------------------+
| 6   | urllib3                |     -      |                       Latest | 1.26.19 - A month ago |
+-----+------------------------+------------+------------------------------+-----------------------+

Failures
********
+-----+------------------------------------------+-----------------------+-------------------------------------+
| #   | Source                                   |        Status         | Resume                              |
+=====+==========================================+=======================+=====================================+
| 1   | ./downloads/numpy-1.9.2-cp34-none-       | unsupported-localpath | Local package is not supported      |
|     | win32.whl                                |                       |                                     |
+-----+------------------------------------------+-----------------------+-------------------------------------+
| 2   | http://wxpython.org/Phoenix/snapshot-bui |    unsupported-url    | Direct package URL is not supported |
|     | lds/wxPython_Phoenix-                    |                       |                                     |
+-----+------------------------------------------+-----------------------+-------------------------------------+
