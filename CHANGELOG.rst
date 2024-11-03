
=========
Changelog
=========

Version 0.4.0 - 2024/11/03
**************************

* Modified analyzer to use **Pypi API** instead of Libraries.io API;
* There is no need anymore for an API key and commands have been modified to remove the
  ``filekey`` argument;
* Fixed RST formatter that failed when asked for failures but there was none;
* Added new argument ``--chunk`` on analyze and report commands. It defines the
  amount of requirements to process before pausing;
* Added optional Rich formatter;
* Added JSON formatter;
* Added CSV formatter;
* Format and Report commands now includes failures table by default, it can still be
  disabled with option ``--no-failures``;
* Updated script to freeze local dependencies;


Version 0.3.0 - 2024/08/27
**************************

* Implemented Pip inclusion directive (aka ``-r dev.txt``) and added a test for it;
* Added commandlines:

  * ``analyze`` to analyze requirements and output a JSON of computed informations;
  * ``format`` to format JSON output from ``analyze`` to RestructuredText tables;
  * ``report`` which merge behaviors of ``analyze`` and ``format`` in a single shot
    without to pipe commands between them;

* Covered everything with tests;
* Covered current version with documentation;


Version 0.2.0 - 2024/07/14
**************************

Added working version of requirement analyzer, parser and package model with
commandline and tests.


Version 0.1.0 - Not released
****************************

First commit with proof of concept with Libraries.io, requests and packaging.
