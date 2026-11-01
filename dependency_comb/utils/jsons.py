import json
import datetime

from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement, SpecifierSet
from packaging.version import Version
from packaging.markers import Marker

from ..package import PackageRequirement


class ExtendedJsonEncoder(json.JSONEncoder):
    """
    Additional support for more object types.

    Usage sample: ::

        json.dumps(..., cls=ExtendedJsonEncoder)

    """
    def default(self, obj):
        # Support for pathlib.Path to a string
        if isinstance(obj, Path):
            return str(obj)
        # Support for set to a list
        if isinstance(obj, set):
            return list(obj)
        # Support for datetime objects
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        # Support for packaging objects
        if isinstance(obj, (Marker, Requirement, SpecifierSet, Version)):
            return str(obj)
        # Support for dependency-comb objects
        if isinstance(obj, PackageRequirement):
            return obj.data()
        # Support for dependency-comb objects
        if isinstance(obj, InvalidRequirement):
            return str(obj)

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
