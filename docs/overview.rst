.. _Pypi API: https://warehouse.pypa.io/api-reference/index.html

.. _overview_intro:

========
Overview
========

How it works
************

The full process of a report with command ``report`` is:

#. Parse given requirements;
#. Store each requirement as an internal ``PackageRequirement`` object;
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

The commands have a ``--cachedir`` argument to store these informations and avoid
performing the same requests on consecutive command executions. This is useful if you
are debugging your project requirements but be aware that there is no way to manage
cache persistence life except removing the cache files.

Finally the `Pypi API`_ is very fast and resilient, however we try to be gentle so the
analyze is done with chunks. Every chunk contains an amount of requirements to analyze
then makes a pause.

The default values for the amount or requirements and pause time (in seconds) has been
made for a reasonable usage. You may configure it differently for faster execution but
please be nice with the `Pypi API`_


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
    standard input.

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

With the following requirements file ``requirements.txt``:

.. include:: ../tests/data_fixtures/pip_syntax/requirements.txt
    :code: text

We can build a report like this: ::

    dependency_comb report requirements.txt

This will print the following output:

.. include:: ../tests/data_fixtures/pip_syntax/formatted_with_failures.rst
    :code: text

.. Note::
    The timedelta here have been computed after an analyze done 25 July 2024.

Also you will have a lots of logging messages about processing, you may mute it with
a command option see :ref:`cli_logging`.

The following sections are the included RestructuredText output sample from before.

.. include:: ../tests/data_fixtures/pip_syntax/formatted_with_failures.rst
