"""
Specific application exceptions.
"""


class DependencyCombBaseException(Exception):
    """
    Exception base.

    You should never use it directly except for test purpose. Instead make or
    use a dedicated exception related to the error context.
    """
    pass


class DependencyCombError(DependencyCombBaseException):
    """
    Basic global error exception.
    """
    pass


class AnalyzerError(DependencyCombError):
    """
    When parser encounter some erroneus content.
    """
    pass


class AnalyzerAPIError(DependencyCombError):
    """
    When analyzer encounter an error from a request from API.

    Attribute ``http_status`` may contains a the HTTP response status code if any.

    Keyword Arguments:
        http_status (integer): HTTP response status code.
    """
    def __init__(self, *args, **kwargs):
        self.http_status = kwargs.pop("http_status", None)
        super().__init__(*args, **kwargs)


class RequirementParserError(DependencyCombError):
    """
    When parser encounter invalid syntax on given content.
    """
    pass
