.. _overview_intro:

========
Overview
========

Unsupported requirement specifiers
**********************************

Direct requirement URL
    We cannot find the package name to get its info from pypi. Requirement will be
    assumed as a failure.

Local package path
    As the same reason than direct requirement URL. Requirement will be
    assumed as a failure.

Pip requirement option
    No requirement option are supported except ``-r``. Requirement will be
    assumed as a failure.

Invalid version
    A version specifier must be valid with
    `packaging library <https://packaging.pypa.io/>`_ which follows
    `PEP 425 <https://peps.python.org/pep-0425/>`_. If requirement specified version
    is valid but have old version with invalid version, these version will be ignored.
    If requirement specified version is invalid it will be assumed as a failure.

Invalid syntax
    Requirement that is not valid with Pip requirement definition format. Requirement
    will be assumed as a failure.

