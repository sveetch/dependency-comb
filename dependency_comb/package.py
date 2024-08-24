from packaging.requirements import InvalidRequirement, Requirement


class PackageRequirement:
    """
    Package requirement object parse given requirement item to get relevant
    informations.

    A package object information is fullfilled in two cycles, firstly the requirement
    parser that is done in PackageRequirement itself then with the data collection and
    computation from the Analyzer. When parsing has failed, all attributes depending
    from collection and computation will be None.

    Arguments:
        source (string): A requirement line to parse.

    Keyword Arguments:
        environment (dict): Optionnal dictionnary of environment variables to use
            with possible specifier marker resolution.

    Attributes:
        source (string): Given requirement source. The source string is expected to be
            stripped from leading whitespaces else it could causes unexpected parsing
            false positive.
        environment (dict): Given environment dictionnary
        status (string): Computed requirement status from parsing process. Status can
            be:

            * ``parsed``: requirement has been properly parsed as supported syntax;
            * ``analyzed``: requirement has been parsed and has been processed by
              the Analyzer;
            * ``unsupported-argument``: unsupported Pip argument, aborted parsing;
            * ``unsupported-localpath``: unsupported local path to package, aborted
              parsing;
            * ``unsupported-url``: unsupported package url, aborted parsing;
            * ``invalid``: invalid requirement syntax (as from PEP425 and PEP440),
              aborted computation from parsed source;
            * ``marker-reject``: Requirement did have marker that does not match
              required environment variables when given, aborted computation from
              parsed source;

            Commonly to get all valid requirements that have been properly analyzed,
            you will just seek for items with status ``analyzed``. ``parsed`` status
            should never occurs when analyzer has been involved.

        marker (packaging.markers.Marker): Marker object parsed from source.
        name (string): Package name parsed from source.
        parsed (packaging.requirements.Requirement): Requirement object parsed from
            source.
        pypi_url (string): Possible package URL collected from API after the parsed
            source.
        repository_url (string): Possible repository URL collected from API after the
            parsed source.
        highest_published (datetime.datetime): Date of the highest release version
            available on Pypi.
        highest_version (packaging.version.Version): Collected highest release version
            available on Pypi.
        lateness (list): List of tuples of version string and datetime for each
            released version that are higher than the resolved version. This means all
            available package versions that could upgraded to.
        resolved_version (string): Resolved release version from specifiers in parsed
            source. Specifiers are used against collected release version
            available on Pypi. This value will be null if no specifier can be found.
            Internally a null value is assumed the requirement can use the latest
            version and so there is no lateness to compute.
        resolved_published (datetime.datetime): Date of the resolved release.
        specifier (packaging.requirements.SpecifierSet): Possible version specifiers
            parsed from source.
        url (string): Possible mirror URL parsed from source.
        extras (set): Possible parsed set of extras environ names from source.
        parsing_error (object): The exception object raise from
            ``packaging.Requirement`` when there was a parsing error.
    """
    STATUS_LABELS = {
        "parsed": "Parsed requirement syntax",
        "analyzed": "Analyzed package informations",
        "unsupported-argument": "Unsupported Pip argument",
        "unsupported-localpath": "Local package is not supported",
        "unsupported-url": "Direct package URL is not supported",
        "invalid": "Invalid syntax",
        "marker-reject": "Rejected by marker evaluation against given environment",
        "unknown": "Unexpected failure",
    }
    VALID_STATUSES = ("parsed", "analyzed")
    PUBLISHED_ATTRIBUTES = [
        "extras", "highest_published", "highest_version", "lateness",
        "marker", "name", "parsed", "pypi_url", "repository_url",
        "source", "specifier", "status", "url", "resolved_version",
        "resolved_published", "parsing_error",
    ]

    def __init__(self, source, environment=None):
        self.source = source
        self.environment = environment

        # All details set to null on default
        self.extras = None
        self.highest_published = None
        self.highest_version = None
        self.lateness = None
        self.marker = None
        self.name = None
        self.parsed = None
        self.pypi_url = None
        self.repository_url = None
        self.specifier = None
        self.status = None
        self.url = None
        self.resolved_version = None
        self.resolved_published = None
        self.parsing_error = None

        # Check if source syntax is supported
        if self.source.startswith("-"):
            self.status = "unsupported-argument"
        elif self.source.startswith((".", "/")):
            self.status = "unsupported-localpath"
        elif self.source.startswith(("http://", "https://")):
            self.status = "unsupported-url"
        else:
            try:
                self.parsed = Requirement(self.source)
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

                # If environment and marker are not empty, evaluate marker against
                # given environment variables to possibly flag source as rejected
                # from marker
                if (
                    self.environment and
                    self.marker and
                    self.marker.evaluate(self.environment) is False
                ):
                    self.status = "marker-reject"
                else:
                    self.status = "parsed"

    def __str__(self):
        return "[{status}] {source}".format(status=self.status, source=self.source)

    def __repr__(self):
        return "<PackageRequirement:{status}> {source}".format(
            status=self.status,
            source=self.source
        )

    @property
    def is_valid(self):
        """
        Express if package has been properly parsed and result to a proper package and
        not unsupported or invalid parsed rule.
        """
        return self.status in self.VALID_STATUSES

    def data(self):
        """
        Return public attributes into a dictionnary.

        Returns:
            dict: The public attributes to publish.
        """
        return {k: getattr(self, k) for k in self.PUBLISHED_ATTRIBUTES}
