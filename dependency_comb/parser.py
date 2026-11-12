import logging

from pathlib import Path

from .exceptions import RequirementParserError
from .models import PackageRequirement
from . import __pkgname__


logger = logging.getLogger(__pkgname__)


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

    def manage_include(self, store, line, basepath, crumb, breadcrumbs=None,
                       environment=None):
        """
        Parse include directive to process its lines.

        Arguments:
            store (list): List where to store included requirements.
            line (string): Content line of the inclusion directive.
            basepath (Path): A directory path where to search for requirement
                inclusions (directive ``-r foo.txt``) from requirements file.
            crumb (Path): Path of the file where the content line comes from.

        Keyword Arguments:
            breadcrumbs (list): A list of Path objects for parent files when content is
                coming from a requirement file. This is used to avoid circular reference
                with included requirement files.
            environment (dict): Environment variables as defined from
                `PEP 508 <https://peps.python.org/pep-0508/>` to use for marker
                evaluations on parsed requirement items.
        """
        inclusion_path = self.get_inclusion_path(line, basepath)

        if inclusion_path:
            if inclusion_path in breadcrumbs:
                msg = (
                    "File '{current}' try to include the parent file "
                    "'{include}' that would lead to a circular reference."
                )
                raise RequirementParserError(
                    msg.format(
                        current=crumb.relative_to(basepath),
                        include=inclusion_path.relative_to(basepath),
                    )
                )

            # Append resolved included requirement files
            store.extend(
                self.parse_recursive_lines(
                    inclusion_path.read_text(),
                    breadcrumbs=breadcrumbs.copy() + [inclusion_path],
                    environment=environment,
                    basepath=basepath
                )
            )

    def manage_duplicate(self, package):
        """
        Find if given package has already been registered and update it if needed.

        Arguments:
            package (PackageRequirement):

        Raises:
            RequirementParserError: In case of conflict with specifier.

        Returns:
            boolean: Returns True if package is a duplicate of a previously parsed one
            else False. A duplicate package is ignored from collection but may alter
            the initial package specifier.
        """
        if package.name not in self.package_registry:
            self.package_registry[package.name] = package
            return False
        else:
            # TODO: We also have to store every duplicate coords to make
            # table in analyze then it can be included in report
            # Or we keep storing requiremnt with a status "duplicate" ?
            if package.origin:
                msg = (
                    "Duplicate requirement for '{name}' found at line "
                    "{lineno} from '{origin}'."
                )
            else:
                msg = (
                    "Duplicate requirement for '{name}' found at line "
                    "{lineno}."
                )

            logger.warning(
                msg.format(
                    origin=package.origin,
                    lineno=package.lineno,
                    name=package.name
                )
            )

            # Check current specifier against registered one
            combined_specifier = (
                self.package_registry[package.name].specifier & package.specifier
            )
            print(
                "💚 Combined specifier:",
                self.package_registry[package.name].specifier,
                "&",
                package.specifier,
                "=",
                combined_specifier,
                combined_specifier.is_unsatisfiable()
            )

            if combined_specifier.is_unsatisfiable():
                msg = "Requirement specifier conflict"
                raise RequirementParserError(msg)
            else:
                self.package_registry[package.name].specifier = combined_specifier

            return True

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
        crumb = breadcrumbs[-1] if breadcrumbs else None

        resolved = []
        for lineno, line in enumerate(content.splitlines(), start=1):
            # Build origin according to crumb and basepath
            origin = crumb if crumb else None
            if origin and basepath:
                origin = origin.relative_to(basepath)

            # Ignore empty lines and comment lines
            if not line.strip() or line.strip().startswith("#"):
                continue

            # Inclusion directive to resolve
            elif basepath and line.strip().startswith("-r "):
                self.manage_include(
                    resolved,
                    line,
                    basepath,
                    crumb,
                    breadcrumbs=breadcrumbs,
                    environment=environment,
                )

            # Everything else (valid, invalid, unsupported, etc..), package parser
            # will process it
            else:
                # Create package requirement object from parsed line
                package = PackageRequirement(
                    line.strip(),
                    origin=origin,
                    lineno=lineno,
                    environment=environment,
                )

                # Evaluate possible duplicate requirement
                is_duplicate = False
                if package.status == "parsed":
                    is_duplicate = self.manage_duplicate(package)

                # Store package
                if not is_duplicate:
                    resolved.append(package)

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

        # Open a new registry where to store accepted packages with their specifier
        # that is used to avoid duplicate and conflicts
        #TODO: Calling 'parse_recursive_lines' directly will cause AttributeError
        self.package_registry = {}

        return self.parse_recursive_lines(
            content,
            breadcrumbs=[path] if path else [],
            environment=environment,
            basepath=basepath
        )
