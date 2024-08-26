
=========
Changelog
=========

Version 0.3.0 - Unreleased
**************************

* Implemented Pip inclusion directive (aka ``-r dev.txt``) and added a test for it;
* Added commandlines:

  * ``analyze`` to analyze requirements and output a JSON of computed informations;
  * ``format`` to format JSON output from ``analyze`` to RestructuredText tables;
  * ``report`` which merge behaviors of ``analyze`` and ``format`` in a single shot
    without to pipe commands between them;

* Covered everything with tests;


Version 0.2.0 - 2024/07/14
**************************

Added working version of requirement analyzer, parser and package model with
commandline and tests.


Version 0.1.0 - Not released
****************************

First commit with proof of concept with Libraries.io, requests and packaging.
