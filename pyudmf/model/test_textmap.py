#!/usr/bin/env python3

from decimal import Decimal

import pytest

from pyudmf.grammar.tu import TranslationUnit, Assignment, Block
from pyudmf.model.factory import ast2textmap
from pyudmf.model.textmap import Textmap, Vertex, Linedef, Sector, Sidedef, Thing
from pyudmf.model.visage import SladeVisage


@pytest.fixture
def sample_ast() -> TranslationUnit:
    return TranslationUnit(
        Assignment("namespace", "zdoom"),
        Block("thing", [
            Assignment("x", Decimal('32.000')),
            Assignment("y", Decimal('32.000')),
            Assignment("type", 1),
        ]),
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
        Block("sidedef", [
            Assignment("sector", 0),
            Assignment("texturemiddle", "MARBFACE"),
        ]),
        Block("sidedef", [
            Assignment("sector", 0),
            Assignment("texturemiddle", "MARBFACE"),
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


def test_ast2textmap(sample_ast, sample_textmap):
    returned = ast2textmap(sample_ast)

    assert sample_textmap == returned


def test_textmap2ast(sample_textmap, sample_ast):
    visage = SladeVisage()
    returned = visage.textmap2ast(sample_textmap)

    str(returned)

    assert len(sample_ast) == len(returned)
    assert [x.identifier for x in sample_ast] == [x.identifier for x in returned]


def test_bijection(sample_textmap):
    visage = SladeVisage()
    returned_textmap = ast2textmap(visage.textmap2ast(sample_textmap))
    assert returned_textmap == sample_textmap
