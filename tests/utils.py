from collections import namedtuple
from os import getenv

import pytest
from freezegun import freeze_time

from dependency_comb.analyzer import DependenciesAnalyzer


API_ENABLED_ENVVAR = "COMB_TEST_API_ENABLED"


# Condition to enable API request depends from environment variable
skip_api_condition = getenv(API_ENABLED_ENVVAR, default="").strip().lower() != "true"


# Named tuple to contain analyzer results from an inspection
BuiltAnalyze = namedtuple(
    "BuiltAnalyze",
    ["packages", "statistics"],
    defaults=[[], {}]
)


def format_to_multline_str(content):
    """
    Shortand to format table output to a multiline string suitable for expected
    assertions.

    Each line will contain a Flake8 bypass code for "line too long".

    This is mostly an helper to rewrite test data fixtures during development.

    Arguments:
        content (string): The content to format.

    Returns:
        string: Formatted content.
    """
    total = len(content.splitlines())
    return "\n".join(
        [
            '"""{source}{newline}"""  # noqa: E501'.format(
                source=l.replace('"', '\\"'),
                newline="\\n" if i < total else "",
            )
            for i, l in enumerate(content.splitlines(), start=1)
        ]
    )


def analyze_builder(settings, filename):
    """
    A shortcut method to build an analyzer with a requirement file from data fixtures.

    All requirement items will have an origin.

    Returns:
        namedtuple: A nametuple including analyzer 'packages' and 'statistics'.
    """
    analyzer = DependenciesAnalyzer(cachedir=settings.apicache_path)

    requirements_path = settings.fixtures_path / "requirements" / filename

    packages = analyzer.inspect(
        requirements_path.read_text(),
        path=requirements_path,
        basepath=requirements_path.parent.resolve()
    )

    return BuiltAnalyze(packages=packages, statistics=analyzer.statistics)


@pytest.fixture(scope="function")
@freeze_time("2024-07-25 10:00:00")
def complete_analyze(settings):
    """
    A test fixture to build an analyze for 'complete.txt' requirements.

    Returns:
        namedtuple: A nametuple including analyzer 'packages' and 'statistics'.
    """
    return analyze_builder(settings, "complete.txt")


@pytest.fixture(scope="function")
@freeze_time("2024-07-25 10:00:00")
def minimal_analyze(settings):
    """
    A test fixture to build an analyze for 'minimal.txt' requirements.

    Returns:
        namedtuple: A nametuple including analyzer 'packages' and 'statistics'.
    """
    return analyze_builder(settings, "minimal.txt")
