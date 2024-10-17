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
    Don't try to set the verbosity level after the ``[COMMAND]``, this option is not
    recognized from commands.


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
    some other tools or script. To quickly get a report see `Report`_ command instead.

Usage: ::

    dependency_comb analyze [OPTIONS] SOURCE

    Arguments:

    source
        Pip requirements file to parse and analyze.
        Instead of a file path you can also give a requirements file content from
        standard input using '-'. For example using the Pip freeze output:

            pip freeze | dependency_comb analyze -

        Or to analyze an unique package:

            echo "django==3.2.1" | dependency_comb analyze -

    Options:
    --cachedir DIRPATH  A directory where to look for API request cache. It is
                        looked for cache file per package and if any, avoid any
                        request for a package details. There is not any mechanic
                        to invalidate or update cache except than to remove
                        cache files. The given directory path will be created
                        automatically if it does not exists yet.
    --destination FILE  File path destination where to write serialized JSON
                        manifest. If not given the JSON will be sent to standard
                        output.
    --indent INTEGER    Indentation level for JSON output. Default to 4 spaces.
    --pause INTEGER     The time in second to pause before an API requests.
                        Default to 1 second.
    --timeout INTEGER   Timeout in seconds for API requests. The default timeout
                        is set to 15 seconds, set it to 0 to disable timeout.
    --env FILEPATH      A JSON file for some environment variables to give to
                        analyzer. This will be used to resolve specifier
                        markers. If analyzer does not receive any environment
                        variable all specifier markers are ignored (so its
                        requirement is always considered valid).
    -h, --help          Show this message and exit.


Format
******

Format a JSON analyze to a report with tables in RestructuredText format. Default
behavior is to only report the correctly analyzed requirement and ignores everything
else. There is an option to include also a table with requirement analyze failures
(invalid syntax, unsupported syntax, etc..).

.. Hint::
    This command is mostly useful to format an archived analyze and so require usage
    of ``analyze`` before. To quickly get a report see `Report`_ command instead.

Usage: ::

    dependency_comb format [OPTIONS] SOURCE

    Arguments:

    source
        Computed analyze in a JSON file path. Instead of a file path you can also give
        a requirements file content from standard input using '-'. For example:

            dependency_comb analyze requirements.txt | dependency_comb report -

    Options:
    --destination FILE  File path destination where to write serialized JSON
                        manifest. If not given the JSON will be sent to standard
                        output.
    --failures          Include requirement analyze failures in a different
                        table, also each tablewill have its own title.
    -h, --help          Show this message and exit.


Report
******

This command merge behaviors of ``analyze`` and ``format`` to directly get a report
from given requirements.

Usage: ::

    dependency_comb report [OPTIONS] SOURCE

    Arguments:

    source
        Pip requirements file to parse, analyze and report.
        Instead of a file path you can also give a requirements file content from
        standard input using '-'. For example using the Pip freeze output:

            pip freeze | dependency_comb report -

        Or to make a report for an unique package:

            echo "django==3.2.1" | dependency_comb report -

    Options:
    --cachedir DIRPATH  A directory where to look for API request cache. It is
                        looked for cache file per package and if any, avoid any
                        request for a package details. There is not any mechanic
                        to invalidate or update cache except than to remove
                        cache files. The given directory path will be created
                        automatically if it does not exists yet.
    --destination FILE  File path destination where to write serialized JSON
                        manifest. If not given the JSON will be sent to standard
                        output.
    --pause INTEGER     The time in second to pause before an API requests.
                        Default to 1 second.
    --timeout INTEGER   Timeout in seconds for API requests. The default timeout
                        is set to 15 seconds, set it to 0 to disable timeout.
    --env FILEPATH      A JSON file for some environment variables to give to
                        analyzer. This will be used to resolve specifier
                        markers. If analyzer does not receive any environment
                        variable all specifier markers are ignored (so its
                        requirement is always considered valid).
    --failures          Include requirement analyze failures in a different
                        table, also each tablewill have its own title.
    -h, --help          Show this message and exit.
