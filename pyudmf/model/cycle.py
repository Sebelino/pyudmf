#!/usr/bin/env python3

import itertools


class Cycle(object):
    """
    itertools.cycle paired with a length.
    """

    def __init__(self, iterable_sizeable):
        self._length = len(iterable_sizeable)
        self._cycle = itertools.cycle(iterable_sizeable)
        self._tuple = tuple(iterable_sizeable)

    @property
    def cycle(self):
        return self._cycle

    def any_tuple(self):
        """ :return: Any tuple containing the elements of the cycle in the correct order. """
        return self._tuple

    def __next__(self):
        return next(self._cycle)

    def __len__(self):
        return self._length

    def __eq__(self, other: 'Cycle'):
        if self._length != other._length:
            return False
        other_list = other._tuple
        for i in range(self._length):
            if self._tuple == other_list[i:] + other_list[:i]:
                return True
        return False

    def __hash__(self):
        return sum(hash(c) for c in self._tuple)

    def __repr__(self):
        return "Cycle({})".format(self._tuple)
