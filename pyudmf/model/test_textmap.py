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
def sample_textmap() -> Textmap:
    sectors = [
        Sector(0, 128, "CEIL3_3", "CEIL3_3"),
    ]
    sidedefs = [
        Sidedef(sectors[0], "MARBFACE"),
    ]
    vertices = [
        Vertex(0.0, 0.0),
        Vertex(0.0, 128.0),
        Vertex(192.0, 128.0),
        Vertex(192.0, 0.0),
    ]
    linedefs = [
        Linedef(vertices[0], vertices[1], sidedefs[0], blocking=True),
        Linedef(vertices[1], vertices[2], sidedefs[0], blocking=True),
        Linedef(vertices[2], vertices[3], sidedefs[0], blocking=True),
        Linedef(vertices[3], vertices[0], sidedefs[0], blocking=True),
    ]
    things = [
        Thing(1, 32.0, 32.0),
    ]
    return Textmap(
        namespace="zdoom",
        vertices=frozenset(vertices),
        sectors=frozenset(sectors),
        sidedefs=frozenset(sidedefs),
        linedefs=frozenset(linedefs),
        things=things
    )


@pytest.fixture
def sample_visage(sample_textmap, sample_ast) -> Visage:
    return Visage(sample_textmap, sample_ast)


def test_ast2textmap(sample_ast, sample_textmap):
    returned, visage = ast2textmap(sample_ast)

    assert sample_textmap == returned


@pytest.mark.skip
def test_textmap2ast(sample_textmap, sample_ast, sample_visage):
    returned = textmap2ast(sample_textmap, visage=sample_visage)

    assert sample_ast == returned


def test_bijection(sample_textmap):
    returned_textmap, _ = ast2textmap(textmap2ast(sample_textmap))
    assert returned_textmap == sample_textmap
