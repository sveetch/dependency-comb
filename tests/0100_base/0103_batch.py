from dependency_comb.utils.lists import split_to_chunks


def test_split_to_chunks():
    """
    The chunk method should properly split items in a batch of chunks of a certain
    amount.
    """
    # Basic
    assert list(split_to_chunks(range(5), 2)) == [(0, 1), (2, 3), (4,)]
    assert list(split_to_chunks(range(5), 1)) == [(0,), (1,), (2,), (3,), (4,)]

    # With more items
    assert list(split_to_chunks(range(13), 3)) == [
        (0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11), (12,)
    ]

    # When amount size is over the total items length, it just works
    assert list(split_to_chunks(range(4), 7)) == [(0, 1, 2, 3)]

    # When amount is empty, it just return the iterable
    assert list(split_to_chunks(range(4), None)) == [(0, 1, 2, 3)]
    assert list(split_to_chunks(range(4), 0)) == [(0, 1, 2, 3)]

    # When items is empty, it just return an empty list
    assert list(split_to_chunks(list(), None)) == []
