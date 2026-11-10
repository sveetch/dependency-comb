import json
from dataclasses import fields as dataclasses_fields

from ...utils.jsons import ExtendedJsonEncoder


class ExportMixin:
    """
    Abstract to inherit to include some methods to implement model object export to
    dictionnary or JSON.

    To ignore some attribute (like parent to avoid circular reference error) you will
    need to implement the ``EXPORT_PRIVATES`` attribute: ::

        EXPORT_PRIVATES: ClassVar[tuple[str]] = (...)

    You may also add some class properties with ``EXPORT_PROPERTIES`` attribute: ::

        EXPORT_PROPERTIES: ClassVar[tuple[str]] = (...)

    Its value is a list of field names to ignore from export, commonly used for
    parenting object to avoid recursion error.
    """
    def get_serialized_field_names(self, allows_only=None):
        """
        Get the list of object field names to serialize.

        Keyword Arguments:
            allows_only (list or tuple): Only the fields (or properties) in this list
                will be serialized.

        Returns:
            list: A list of field names.
        """
        allows_only = allows_only or tuple()
        exported_properties = getattr(self, "EXPORT_PROPERTIES", tuple())
        privates = getattr(self, "EXPORT_PRIVATES", tuple())

        names = [f.name for f in dataclasses_fields(self)]

        names = [
            item
            for item in tuple(names) + exported_properties
            if item not in privates
        ]

        if allows_only:
            names = [item for item in names if item in allows_only]

        return names

    def serialize(self, allows_only=None, coerced=False):
        """
        A safe way to convert to a dict without recursion issues.

        Keyword Arguments:
            allows_only (list or tuple): Only the fields (or properties) in this list
                will be serialized. Children objects must support 'allows_only' in
                their serialization.
            coerced (bool): If enabled all values with a method ``serialize()``
                will use it instead of returning model object so you get only pure
                Python builtin types (and not model objects).

        Returns:
            dict: This model object attribute serialized in a dictionnary, items named
                after one of names from EXPORT_PRIVATES won't be in the output.
        """
        return {
            name: (
                getattr(self, name).serialize(coerced=coerced, allows_only=allows_only)
                if coerced is True and hasattr(getattr(self, name), "serialize")
                else getattr(self, name)
            )
            for name in self.get_serialized_field_names(allows_only=allows_only)
        }

    def as_coerced(self, allows_only=None):
        """
        A shortcut to returns the output of ``serialize()`` with ``coerced`` option
        enabled.
        """
        return self.serialize(coerced=True, allows_only=allows_only)

    def as_json(self, allows_only=None):
        """
        Returns the output of ``serialize()`` in a JSON string.
        """
        return json.dumps(
            self.as_coerced(allows_only=allows_only),
            indent=4,
            cls=ExtendedJsonEncoder,
        )
