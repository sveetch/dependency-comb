from pathlib import Path

from .exceptions import RequirementParserError
from .models import PackageRequirement


class RequirementParser:
    """
    Parse a requirements file to resolve each lines as a ``PackageRequirement`` object.

    .. Note::
        Multiline for a requirement directive is not supported.
    """
    def get_inclusion_path(self, line, basepath):
        """
        Find the requirement file to include its content from an inclusion directive.

        Arguments:
            line (string):
            basepath (Path):

        Returns:
            Path: The file path to read for inclusion content.
        """
        parts = line.split()

        # When there is the inclusion argument without a following requirement file
        # path, we just ignore the inclusion line
        if len(parts) < 2:
            return None

        requirement_path = basepath / Path(parts[1])

        if not requirement_path.exists():
            raise RequirementParserError(
                "Unable to find included source: {}".format(requirement_path)
            )

        return requirement_path.resolve()

    def parse_recursive_lines(self, content, breadcrumbs=None, environment=None,
                              basepath=None):
        """
        Recursively parse requirement lines to store them as PackageRequirement objects.

        Inclusion directive are resolved and replaced with their requirements if
        basepath is given. Commentaries and empty lines (starting with ``#``) are
        directly filtered out at this stage.

        Arguments:
            content (string): Requirement lines to parse, possibly with included
                requirement files.

        Keyword Arguments:
            breadcrumbs (list): A list of Path objects for parent files when content is
                coming from a requirement file. This is used to avoid circular reference
                with included requirement files.
            environment (dict): Environment variables as defined from
                `PEP 508 <https://peps.python.org/pep-0508/>` to use for marker
                evaluations on parsed requirement items.
            basepath (Path): A directory path where to search for requirement
                inclusions (directive ``-r foo.txt``) from requirements file. If not
                given inclusions will be ignored and PackageRequirement will assume
                them as an unsupported argument. This should always be given for
                content file.

        Returns:
            list: List of PackageRequirement objects for all involved requirements.
        """
        breadcrumbs = [] if breadcrumbs is None else breadcrumbs
        # The path of requirements source we are currently parsing
        current_crumb = breadcrumbs[-1] if breadcrumbs else None

        resolved = []
        for lineno, line in enumerate(content.splitlines(), start=1):
            # Ignore empty lines and comment lines
            if not line.strip() or line.strip().startswith("#"):
                continue

            # Inclusion directive to resolve
            elif basepath and line.strip().startswith("-r "):
                inclusion_path = self.get_inclusion_path(line, basepath)

                if inclusion_path:
                    if inclusion_path in breadcrumbs:
                        msg = (
                            "File '{current}' try to include the parent file "
                            "'{include}' that would lead to a circular reference."
                        )
                        raise RequirementParserError(
                            msg.format(
                                current=current_crumb.relative_to(basepath),
                                include=inclusion_path.relative_to(basepath),
                            )
                        )

                    # Append resolved included requirement files
                    resolved.extend(self.parse_recursive_lines(
                        inclusion_path.read_text(),
                        breadcrumbs=breadcrumbs.copy() + [inclusion_path],
                        environment=environment,
                        basepath=basepath
                    ))

            # Everything else (valid, invalid, unsupported, etc..), package parser
            # will process it
            else:
                # Build origin according to crumb and basepath
                origin = None
                if current_crumb and basepath:
                    origin = current_crumb.relative_to(basepath)
                elif current_crumb and not basepath:
                    origin = current_crumb

                # Store parsed requirement line
                resolved.append(
                    PackageRequirement(
                        line.strip(),
                        origin=origin,
                        lineno=lineno,
                        environment=environment,
                    )
                )

        return resolved

    def parse_requirements(self, content, path=None, sourcepath=None,
                           environment=None, basepath=None):
        """
        Load content as requirements.

        Arguments:
            content (string or Path): Content to load. Either a string for a content
                to parse or a Path object to open and read as a content to parse. If
                it is a string, the ``path`` argument should be given with the source
                path as it is used to avoid circular reference.

        Keyword Arguments:
            path (Path): Source content file path. If ``content`` was a Path object,
                this argument value is not used.
            environment (dict): Environment variables as defined from
                `PEP 508 <https://peps.python.org/pep-0508/>` to use for marker
                evaluations on parsed requirement items.
            basepath (Path): A directory path where to search for requirement
                inclusions (directive ``-r foo.txt``) from requirements file. If not
                given, all inclusions will be ignored and PackageRequirement will assume
                it as an unsupported argument.

        Returns:
            list: List of PackageRequirement objects for all involved requirements.
        """
        if isinstance(content, Path):
            path = content
            content = path.read_text()

        return self.parse_recursive_lines(
            content,
            breadcrumbs=[path] if path else [],
            environment=environment,
            basepath=basepath
        )
