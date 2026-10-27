import datetime

import pytest

from dependency_comb.utils.dates import safe_isoformat_parse


@pytest.mark.parametrize("source, expected", [
    ("2022-10-29T14:15:57.755859Z", datetime.datetime(2022, 10, 29, 14, 15, 57)),
    ("2022-10-29T14:15:57Z", datetime.datetime(2022, 10, 29, 14, 15, 57)),
])
def test_safe_isoformat_parse(source, expected):
    """
    Should parse a string that is expected to be a datetime in ISO format
    """
    assert safe_isoformat_parse(source) == expected
