#!/usr/bin/env python3

from decimal import Decimal

import pytest

from pyudmf.grammar.tu import TranslationUnit, Assignment, Block
from pyudmf.model.factory import ast2textmap, textmap2ast
from pyudmf.model.textmap import Textmap, Vertex, Linedef, Sector, Sidedef, Thing
from pyudmf.model.visage import Visage


@pytest.fixture
def sample_ast() -> TranslationUnit:
    return TranslationUnit(
        Assignment("namespace", "zdoom"),
        Block("vertex", [
            Assignment("x", Decimal('0.000')),
            Assignment("y", Decimal('0.000')),
        ]),
        Block("vertex", [
            Assignment("x", Decimal('0.000')),
            Assignment("y", Decimal('128.000')),
        ]),
        Block("vertex", [
            Assignment("x", Decimal('192.000')),
            Assignment("y", Decimal('128.000')),
        ]),
        Block("vertex", [
            Assignment("x", Decimal('192.000')),
            Assignment("y", Decimal('0.000')),
        ]),
        Block("linedef", [
            Assignment("v1", 0),
            Assignment("v2", 1),
            Assignment("sidefront", 0),
            Assignment("blocking", True),
        ]),
        Block("linedef", [
            Assignment("v1", 1),
            Assignment("v2", 2),
            Assignment("sidefront", 0),
            Assignment("blocking", True),
        ]),
        Block("linedef", [
            Assignment("v1", 2),
            Assignment("v2", 3),
            Assignment("sidefront", 0),
            Assignment("blocking", True),
        ]),
        Block("linedef", [
            Assignment("v1", 3),
            Assignment("v2", 0),
            Assignment("sidefront", 0),
            Assignment("blocking", True),
        ]),
        Block("sidedef", [
            Assignment("sector", 0),
            Assignment("texturemiddle", "MARBFACE"),
        ]),
        Block("sector", [
            Assignment("texturefloor", "CEIL3_3"),
            Assignment("textureceiling", "CEIL3_3"),
            Assignment("heightceiling", 128),
        ]),
        Block("thing", [
            Assignment("x", Decimal('32.000')),
            Assignment("y", Decimal('32.000')),
            Assignment("type", 1),
        ]),
    )


@pytest.fixture
def vertices():
    return [
        Vertex(0.0, 0.0),
        Vertex(0.0, 128.0),
        Vertex(192.0, 128.0),
        Vertex(192.0, 0.0),
    ]


@pytest.fixture
def sectors():
    return [
        Sector(0, 128, "CEIL3_3", "CEIL3_3"),
    ]


@pytest.fixture
def sidedefs(sectors):
    return [
        Sidedef(sectors[0], "MARBFACE"),
    ]


@pytest.fixture
def linedefs(vertices, sidedefs):
    return [
        Linedef(vertices[0], vertices[1], sidedefs[0], blocking=True),
        Linedef(vertices[1], vertices[2], sidedefs[0], blocking=True),
        Linedef(vertices[2], vertices[3], sidedefs[0], blocking=True),
        Linedef(vertices[3], vertices[0], sidedefs[0], blocking=True),
    ]


@pytest.fixture
def things():
    return [
        Thing(1, 32.0, 32.0),
    ]


@pytest.fixture
def sample_textmap(vertices, sectors, sidedefs, linedefs, things) -> Textmap:
    return Textmap(
        namespace="zdoom",
        vertices=frozenset(vertices),
        sectors=frozenset(sectors),
        sidedefs=frozenset(sidedefs),
        linedefs=frozenset(linedefs),
        things=things
    )


@pytest.fixture
def sample_visage(sample_textmap, vertices, sectors, sidedefs, linedefs, things) -> Visage:
    dct = {
        'namespace': {'global_index': 0},
        'vertices': {
            vertices[0]: {'global_index': 1},
            vertices[1]: {'global_index': 2},
            vertices[2]: {'global_index': 3},
            vertices[3]: {'global_index': 4},
        },
        'sectors': {
            sectors[0]: {'global_index': 10},
        },
        'sidedefs': {
            sidedefs[0]: {'global_index': 9},
        },
        'linedefs': {
            linedefs[0]: {'global_index': 5},
            linedefs[1]: {'global_index': 6},
            linedefs[2]: {'global_index': 7},
            linedefs[3]: {'global_index': 8},
        },
        'things': {
            things[0]: {'global_index': 11},
        },
    }
    return Visage(sample_textmap, dct)


def test_ast2textmap(sample_ast, sample_textmap):
    returned, visage = ast2textmap(sample_ast)

    assert sample_textmap == returned


def test_textmap2ast_full(sample_textmap, sample_ast, sample_visage):
    returned = textmap2ast(sample_textmap, visage=sample_visage)

    str(returned)

    assert [type(e) for e in sample_ast] == [type(e) for e in returned]

    a = [e.identifier for e in sample_ast if isinstance(e, Block)]
    b = [e.identifier for e in returned if isinstance(e, Block)]
    assert a == b


@pytest.mark.skip
def test_textmap2ast(sample_textmap, sample_ast, sample_visage):
    returned = textmap2ast(sample_textmap, visage=sample_visage)

    assert sample_ast == returned


def test_bijection(sample_textmap):
    returned_textmap, _ = ast2textmap(textmap2ast(sample_textmap))
    assert returned_textmap == sample_textmap
