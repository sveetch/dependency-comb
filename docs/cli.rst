.. _cli_intro:

============
Command line
============

Usage
*****

Once installed on your system you can use the tool directly: ::

    dependency-comb

This entrypoint don't perform any tasks, see its available commands.


.. _cli_logging:

Logging level
-------------

The entrypoint is where you can set the verbosity level from commands like this: ::

    dependency-comb -v 0 [COMMAND]..

The value is an integer between 0 and 5 where 0 is to mute everything except critical
errors and 5 is to output everything.

.. Note::
    Don't try to set the verbosity level after the ``[COMMAND]``, the option won't
    be recognized.


.. _cli_cmd_help:

Help
****

There is a base tool help for global options and available commands: ::

    dependency-comb -h

And if you use ``-h`` after a command name you will get its specific help: ::

    dependency-comb [COMMAND] -h


.. _cli_cmd_report:

Report
******

This command proceed to an analyze of requirements and format it to a report.

Usage:

.. include:: ./_static/command_helps/report.txt
    :code: text
