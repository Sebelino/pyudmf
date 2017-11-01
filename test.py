#!/usr/bin/env python

from udmfscale import parse_udmf


def test_parse_udmf__empty__empty_list():
    returned = parse_udmf("")
    assert returned == []
