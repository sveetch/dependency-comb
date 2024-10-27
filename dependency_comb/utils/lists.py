from itertools import islice


def split_to_chunks(items, size):
    """
    Split an iterable in chunks of a certain amount.

    Sample usage: ::

        >>> list(split_to_chunks(range(5), 2))
        [(0, 1), (2, 3), (4,)]

    Stealed from https://stackoverflow.com/a/22045226

    Arguments:
        items (iterable): An iterable of items to split in chunks.
        size (integer): Amount of items to place in each chunks.

    Returns:
        iterable: An iterable of chunks.
    """
    if not items:
        return []

    if not size:
        return [tuple(items)]

    items = iter(items)

    return iter(lambda: tuple(islice(items, size)), ())
