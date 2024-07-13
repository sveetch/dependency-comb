.. _Python: https://www.python.org/
.. _Click: https://click.palletsprojects.com
.. _requests: https://www.python.org/
.. _semantic-version: https://www.python.org/
.. _humanize: https://www.python.org/
.. _packaging: https://www.python.org/
.. _Libraries.io: https://www.python.org/


===============
Dependency comb
===============

A tool to analyze requirements lateness with `Libraries.io`_ API.

The plan is to have a tool to read project requirements and check their informations
from `Libraries.io`_ API and build a report about packages activities. The report will
contains some informations to see if versions from requirements is below the latest
packages release versions, last time since the last release and how many versions
behind the latest release.

This can be especially useful when auditing an existing project.


Dependencies
************

* `Python`_>=3.8;
* `Click`_>=8.0;
* `requests`_>=2.32.3;
* `semantic-version`_>=2.10.0;
* `humanize`_>=4.9.0;
* `packaging`_>=24.0;


Links
*****

* Read the documentation on `Read the docs <https://dependency-comb.readthedocs.io/>`_;
* Download its `PyPi package <https://pypi.python.org/pypi/dependency-comb>`_;
* Clone it on its `Github repository <https://github.com/sveetch/dependency-comb>`_;
