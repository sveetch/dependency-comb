import json
import datetime

from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement, SpecifierSet
from packaging.version import Version
from packaging.markers import Marker


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
        # Support for date and time objects
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        # Support for timedelta objects
        if isinstance(obj, (datetime.timedelta)):
            return obj.total_seconds()
        # Support for packaging objects
        if isinstance(obj, (Marker, Requirement, SpecifierSet, Version)):
            return str(obj)
        # Support for dependency-comb objects
        if isinstance(obj, InvalidRequirement):
            return str(obj)

        # Support for models without to import them (from their specific class name)
        # NOTE: This is to be as a last resort
        if hasattr(obj, "serialize"):
            return obj.serialize()

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
