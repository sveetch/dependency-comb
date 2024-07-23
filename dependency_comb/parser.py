from pathlib import Path

from .exceptions import RequirementParserError
from .package import PackageRequirement


class RequirementParser:
    """
    Parse a requirements file content to resolve each requirement line as a
    ``PackageRequirement`` object.

    Multiline directive is not supported.
    """
    def get_nested_content(self, line, basepath):
        """
        Find the requirement file to include its content from an inclusion directive.

        Arguments:
            line (string):
            basepath (Path):

        Returns:
            string: The file content to include.
        """
        parts = line.split()

        # When there is the inclusion argument without following requirement file path.
        if len(parts) < 2:
            return None

        requirement_path = basepath / Path(parts[1])

        if not requirement_path.exists():
            raise RequirementParserError(
                "Unable to find included source: {}".format(requirement_path)
            )

        return requirement_path.read_text()

    def parse_recursive_lines(self, content, environment=None, basepath=None):
        """
        Recursively parse requirement lines to store them as PackageRequirement objects.

        Inclusion directive are resolved and replaced with their requirements if
        basepath is given. Commentaries and empty lines (starting with ``#``) are
        directly filtered out at this stage.

        .. Warning::
            There is no check about circular import in inclusions (like a ``base.txt``
            requirement including ``dev.txt`` requirement which include ``base.txt``).

        Arguments:
            content (string or Path): Content to load. Either a string for the content
            to parse or a Path object to open and read as content to parse.

        Keyword Arguments:
            environment (dict): Environment variables as defined from
                `PEP 508 <https://peps.python.org/pep-0508/>` to use for marker
                evaluations on parsed requirement items.
            basepath (Path): A directory path where to search for requirement
                inclusions (directive ``-r foo.txt``) from requirements file. If not
                given inclusions will be ignored and PackageRequirement will assume it
                as an unsupported argument.

        Returns:
            list: List of PackageRequirement objects for all involved requirements.
        """
        if isinstance(content, Path):
            content = content.read_text()

        resolved = []
        for line in content.splitlines():
            # Always ignore empty lines and commentaries
            if not line.strip() or line.strip().startswith("#"):
                continue
            # Inclusion directive to resolve
            elif basepath and line.strip().startswith("-r "):
                inclusion = self.get_nested_content(line, basepath)
                if inclusion:
                    resolved.extend(self.parse_recursive_lines(
                        inclusion,
                        environment=environment,
                        basepath=basepath
                    ))
            # Default behavior for everything else (that can be valid, invalid,
            # unsupported, etc..), package parser will take it in charge
            else:
                resolved.append(
                    PackageRequirement(line.strip(), environment=environment)
                )

        return resolved

    def parse_requirements(self, content, environment=None, basepath=None):
        """
        Load content as requirements.

        Arguments:
            content (string or Path): Content to load. Either a string for the content
            to parse or a Path object to open and read as content to parse.

        Keyword Arguments:
            environment (dict): Environment variables as defined from
                `PEP 508 <https://peps.python.org/pep-0508/>` to use for marker
                evaluations on parsed requirement items.
            basepath (Path): A directory path where to search for requirement
                inclusions (directive ``-r foo.txt``) from requirements file. If not
                given inclusions will be ignored and PackageRequirement will assume it
                as an unsupported argument.

        Returns:
            list: List of PackageRequirement objects for all involved requirements.
        """
        # Parse each line as a requirement except empty line and comments
        return self.parse_recursive_lines(
            content,
            environment=environment,
            basepath=basepath
        )
