.. _cli_intro:

============
Command line
============

Usage
*****

Once installed on your system you can use the tool directly: ::

    dependency_comb

This entrypoint don't perform any tasks, see its available commands.

.. _cli_logging:

Logging level
-------------

The entrypoint is where you can set the verbosity level from commands like this: ::

    dependency_comb -v 0 [COMMAND]..

The value is an integer between 0 and 5 where 0 is to mute everything except critical
errors and 5 is to output everything.

.. Note::
    Don't try to set the verbosity level after the ``[COMMAND]``, the option won't
    be recognized.


Help
****

There is a base tool help for global options: ::

    dependency_comb -h

And if you use ``-h`` after a command name you will get its specific help: ::

    dependency_comb analyze -h

Analyze
*******

Analyze given requirements to build a JSON file with all computed informations from
releases of every valid requirement.

.. Note::
    When no destination are given, the command will output JSON to the standard output
    and so all logging messages are muted to ensure valid JSON output.

.. Hint::
    This command is mostly useful to output an analyze to use in a further way with
    some other tools or scripts. To quickly get a report see `Report`_ command instead.

Usage:

.. include:: ./_static/command_helps/analyze.txt
    :code: text


Format
******

Format a JSON analyze to a report with tables in RestructuredText format. Default
behavior is to only report the correctly analyzed requirement and ignores everything
else. There is an option to include also a table with requirement analyze failures
(invalid syntax, unsupported syntax, etc..).

.. Hint::
    This command is mostly useful to format an archived analyze and so require usage
    of ``analyze`` before. To quickly get a report see `Report`_ command instead.

Usage:

.. include:: ./_static/command_helps/format.txt
    :code: text


Report
******

This command merge behaviors of ``analyze`` and ``format`` to directly get a report
from given requirements.

Usage:

.. include:: ./_static/command_helps/report.txt
    :code: text
