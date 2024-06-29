from pathlib import Path

from .package import PackageRequirement


class RequirementParser:
    """
    Parse a requirements file content to resolve each requirement line as a
    ``PackageRequirement`` object.
    """
    def parse_requirements(self, content, environment=None):
        """
        Load content as requirements.

        Arguments:
            content (string or Path): Content to load. Either a string for the content
            to parse or a Path object to open and read as content to parse.

        Keyword Arguments:
            environment (dict): Environment variables as defined from
                `PEP 508 <https://peps.python.org/pep-0508/>` to use for marker
                evaluations on parsed requirement items.

        """
        if isinstance(content, Path):
            content = content.read_text()

        # Parse each line as a requirement except empty line and comments
        return [
            PackageRequirement(line.strip(), environment=environment)
            for line in content.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
