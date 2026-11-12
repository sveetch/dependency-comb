import datetime
from pathlib import Path
from dataclasses import dataclass, field as dataclasses_field
from typing import Any, ClassVar

from packaging.markers import Marker
from packaging.requirements import InvalidRequirement, SpecifierSet, Requirement
from packaging.version import Version

from .mixins.export import ExportMixin


STATUS_LABELS = {
    "parsed": "Parsed requirement syntax",
    "analyzed": "Analyzed package informations",
    "unsupported-argument": "Unsupported Pip argument",
    "unsupported-localpath": "Local package is not supported",
    "unsupported-url": "Direct package URL is not supported",
    "invalid": "Invalid syntax",
    "marker-reject": "Rejected by marker evaluation against given environment",
    "duplicate": "Duplicate package requirement",
    "unknown": "Unexpected failure",
}

VALID_STATUSES = ("parsed", "analyzed")


@dataclass
class PackageRequirement(ExportMixin):
    """
    Package requirement object parse given requirement item to get relevant
    informations.

    A package object information is fullfilled in two cycles, firstly the requirement
    parser that is done in PackageRequirement itself then with the data collection and
    computation from the Analyzer. When parsing has failed, all attributes depending
    from collection and computation will be null.

    The requirement parser will only set value on the following attributes:

    * ``name``;
    * ``url``;
    * ``extras``;
    * ``specifier``;
    * ``marker``;

    All other attributes are in charge of analyzer.

    Arguments:
        source (string): A requirement line to parse.

    Keyword Arguments:
        environment (dict): Optionnal dictionnary of environment variables to use
            for specifier marker resolution. If requirements involve markers and this
            attribute is empty, requirements with markers will fail on parsing. When
            environment is empty, all markers are assumed to be valid.

    Attributes:
        source (string): Given requirement source. The source string is expected to be
            stripped from leading whitespaces else it could causes unexpected parsing
            false positive.
        origin (pathlib.Path): If source comes from a requirement file this will be
            its Path object. Else it will be null.
        lineno (integer): Line number of source from requirement file, if source does
            not come from a requirement file it will be a zero value.
        environment (dict): Given environment dictionnary
        status (string): Computed requirement status from parsing processes. Status can
            be:

            * ``unsupported-argument``: unsupported Pip argument, aborted parsing;
            * ``unsupported-localpath``: unsupported local path to package, aborted
              parsing;
            * ``unsupported-url``: unsupported package url, aborted parsing;
            * ``invalid``: invalid requirement syntax (as from PEP425 and PEP440),
              aborted computation from parsed source;
            * ``marker-reject``: Requirement have marker that does not match
              required environment variables when given, aborted computation from
              parsed source;
            * ``parsed``: requirement has been properly parsed as supported syntax. This
              is a temporary status that analyzer will overwrite to another one;
            * ``duplicate``: When the package requirement has already been parsed
              previously from another line. The requirement won't be analyzed but its
              specifier may update the specifier of the initial requirement occurence;
            * ``analyzed``: requirement has been parsed and has been processed by
              the Analyzer;

            Commonly to get all valid requirements that have been properly analyzed,
            you will just seek for items with status ``analyzed``.

            The status ``duplicate`` and ``analyzed`` are only applied from the
            analyzer.

        marker (packaging.markers.Marker): Marker object parsed from source.
        name (string): Package name parsed from source.
        parsed (packaging.requirements.Requirement): Requirement object parsed from
            source.
        pypi_url (string): Possible package URLs collected from API after the parsed
            source.
        repository_url (string): Possible repository URL collected from API after the
            parsed source.
        highest_published (datetime.datetime): Date of the highest release version
            available on Pypi.
        highest_version (packaging.version.Version): Collected highest release version
            available on Pypi.
        highest_delta (datetime.timedelta): Time period between current date and
            ``highest_published``.
        lateness (list): List of tuples of version string and datetime for each
            released version that are higher than the resolved version. This means all
            available package versions that could be upgraded to.
        resolved_version (string): Resolved release version from specifiers in parsed
            source. Specifiers are used against collected release version
            available on Pypi. This value will be null if no specifier can be found.
            Internally a null value is assumed the requirement can use the latest
            version and so there is no lateness to compute.
        resolved_published (datetime.datetime): Date of the resolved release.
        resolved_delta (datetime.timedelta): Time period between current date and
            ``resolved_published``.
        specifier (packaging.requirements.SpecifierSet): Possible version specifiers
            parsed from source.
        url (string): Possible mirror URL parsed from source.
        extras (set): Possible parsed set of extras environ names from source.
        parsing_error (object): The exception object raise from
            ``packaging.Requirement`` when there was a parsing error.
    """
    EXPORT_PRIVATES: ClassVar[tuple[str]] = ("environment",)
    EXPORT_PROPERTIES: ClassVar[tuple[str]] = ()

    source: str
    origin: Path = None
    lineno: int = 0
    environment: dict = dataclasses_field(repr=False, default=None)
    extras: set = dataclasses_field(repr=False, default=None)
    highest_published: datetime.datetime = None
    highest_version: Version = None
    highest_delta: datetime.timedelta = None
    lateness: list = dataclasses_field(repr=False, default=None)
    marker: Marker = None
    name: str = None
    parsed: Requirement = None
    pypi_url: str = None
    repository_url: str = None
    specifier: SpecifierSet = None
    status: str = None
    url: str = None
    resolved_version: Version = None
    resolved_published: datetime.datetime = None
    resolved_delta: datetime.timedelta = None
    parsing_error: Any = None

    def __post_init__(self):
        # Check source syntax validity
        if self.source.startswith("-"):
            self.status = "unsupported-argument"
        elif self.source.startswith((".", "/")):
            self.status = "unsupported-localpath"
        elif self.source.startswith(("http://", "https://")):
            self.status = "unsupported-url"
        # Assume we can parse the source
        else:
            try:
                # Parse source with possible comment part removed
                self.parsed = Requirement(self.source.split(" #")[0].strip())
            except InvalidRequirement as e:
                self.status = "invalid"
                self.parsing_error = e
            else:
                # Initialize basic details from parsed source
                self.name = self.parsed.name
                self.url = self.parsed.url
                self.extras = self.parsed.extras
                self.specifier = self.parsed.specifier
                self.marker = self.parsed.marker

                # If environment and marker are not empty, evaluate the marker with
                # environment variables to possibly set source as rejected
                # from marker
                if (
                    self.environment and
                    self.marker and
                    self.marker.evaluate(self.environment) is False
                ):
                    self.status = "marker-reject"
                # Finally the requirement has been correctly parsed
                else:
                    self.status = "parsed"

    @property
    def is_valid(self):
        """
        Express if package has been properly parsed and result to a proper package.
        Unsupported syntax or invalid parsing are never considered as valid.
        """
        return self.status in VALID_STATUSES
