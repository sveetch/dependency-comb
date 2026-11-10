.. _Pypi API: https://warehouse.pypa.io/api-reference/index.html

.. _overview_intro:

========
Overview
========

.. _overview_how:

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

.. Note::
    There is no need for analyzed project or packages to be installed because the
    analyze only needs informations from `Pypi API`_.

.. _overview_api:

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


.. _overview_includes:

Requirements include
********************

A requirement file can include other requirement files using the Pip option ``-r ...``,
this is supported from analyzer. However remember that relative requirement file paths
are resolved from the main requirement file path or from your current position path if
you given requirements from standard input.


.. _overview_marker:

Marker expression
*****************

`Marker <https://packaging.pypa.io/en/stable/markers.html>`_ expression is supported
in package requirement definition but is only evaluated if environment is given. If
environment is not given all markers are just ignored and the requirement is considered
valid.

Commands :ref:`cli_cmd_analyze` and :ref:`cli_cmd_report` allow to give an
environment.

Here is a JSON sample of an advanced environment: ::

    {
        "implementation_name": "cpython",
        "implementation_version": "3.13.3",
        "os_name": "posix",
        "platform_machine": "x86_64",
        "platform_release": "6.14.0-37-generic",
        "platform_system": "Linux",
        "platform_version": "#37-Ubuntu SMP PREEMPT_DYNAMIC Fri Nov 14 22:10:32 UTC 2025",
        "python_full_version": "3.13.3",
        "platform_python_implementation": "CPython",
        "python_version": "3.13",
        "sys_platform": "linux"
    }

Not all these variables are needed but it finally depends from your requirements.


.. _overview_unsupported:

Unsupported requirement specifiers
**********************************

Here we describe unsupported specified with a reason. An unsupported specifier will just
make a requirement assumed as invalid.

Direct requirement URL
    Because we cannot determine the package name to get its info from pypi.

Local package path
    As the same reason than direct requirement URL.

Pip requirement option
    No requirement option are supported except ``-r``.

Invalid version
    A version specifier must be valid with
    `packaging library <https://packaging.pypa.io/>`_. If requirement specified version
    is valid but have old versions with invalid version format, these version will be
    ignored. If requirement specified version is invalid it will be assumed as a
    failure.

Invalid syntax
    Requirement that is not valid with Pip requirement definition format.

.. Hint::
    You can see every failures and warning with the ``report`` command with options
    for maximum verbosity level and enable failures inclusion.

    The command ``analyze`` can do it also but not when used to output JSON to the
    standard input.


.. _overview_demo:

Demonstration
*************

With the following requirements file ``requirements.txt``:

.. include:: ../tests/data_fixtures/requirements_basic.txt
    :code: text

We can build a report like this: ::

    dependency_comb report requirements.txt

This will print the following output:

.. include:: ../tests/data_fixtures/formatted/with_failures.rst
    :code: text

.. Note::
    The timedelta here have been computed after an analyze done 25 July 2024.

Also you will have a lots of logging messages about processing, you may mute it with
a command option see :ref:`cli_logging`.

The following sections are the included RestructuredText output sample from before.

.. include:: ../tests/data_fixtures/formatted/with_failures.rst
