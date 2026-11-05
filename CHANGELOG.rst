
=========
Changelog
=========

Planned
*******

* [ ] Uniqueness on final package list is not enforced #8;
* [ ] Add optional extra requirement 'rich-click';
* [ ] Reporter command should exit with code 1 if there is failure and new option
  "--exit-1" is enabled, related to #2;
* [ ] Log warning like "Ignored invalid version number 'rc1' for package 'django-axes'"
  should be a debug instead;
* [ ] Reporter is not tested for empty results (alike with Formatter);
* [ ] Add support to read a dump from 'pip-audit' to include security issues. It should
  be done flexible enough to possibly add support also from
  'uv audit --output-format json';
* [ ] Improve report informations and readability

  * [ ] #5;
  * [ ] Add (to format and report cli) a final resume like: ::

        "78 packages, 3 late, 8 failures."

  * [ ] Python version should be included in json, rst and rich formats;
  * [ ] Failures should use more space for long text, it should be in a table in the
    form: ::

        | #id | 'status'
        |     | untruncated 'source'
        |     | 'resume'

Development
***********

* Added templates for Github issues;
* Fixed issue with packages that don't define anything in ``project_urls``;
* Fixed again data fixtures for some delta date changes;
* Fixed JSONFormatter that was not forgotting 'with_failures' argument;
* Reworked Formatter to properly manage when success and failures parts are empty,
  fix #11;
* Changed Rich formatter so the table is not restrained to its panel container and
  package 'name' display are never truncated in analyzes, fix #7;
* Fixed requirement line parser to ignore comment part, fix #6;
* Fixed requirement parser to raise error when there is circular reference in
  included requirement files, fix #4;
* Renamed command from ``dependency_comb`` to ``dependency-comb``, fix #1;
* Upgraded official Python support up to 3.14;
* Updated Tox configuration to match Python support and optional Rich;
* Restructured test data fixtures files;


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
