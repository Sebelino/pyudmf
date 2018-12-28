#!/usr/bin/env python3

from decimal import Decimal

from pyudmf.grammar.tu import TranslationUnit, Assignment, Block
from pyudmf.model.factory import ast2textmap
from pyudmf.model.textmap import Textmap, Vertex, Linedef, Sector, Sidedef, Thing


def test_textmap():
    tu = TranslationUnit(
        Block("vertex", [
            Assignment("x", Decimal(0.0)),
            Assignment("y", Decimal(0.0)),
        ]),
        Block("vertex", [
            Assignment("x", Decimal(0.0)),
            Assignment("y", Decimal(128.0)),
        ]),
        Block("vertex", [
            Assignment("x", Decimal(192.0)),
            Assignment("y", Decimal(128.0)),
        ]),
        Block("vertex", [
            Assignment("x", Decimal(192.0)),
            Assignment("y", Decimal(0.0)),
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
            Assignment("texturefloor", "MFLR8_1"),
            Assignment("textureceiling", "MFLR8_1"),
            Assignment("heightceiling", 128),
        ]),
        Block("thing", [
            Assignment("x", 32.0),
            Assignment("y", 32.0),
            Assignment("type", 1),
        ]),
    )

    returned = ast2textmap(tu)

    sectors = [
        Sector(0, 200, "CEIL3_3", "CEIL3_3"),
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
        Linedef(vertices[0], vertices[1], sidedefs[0]),
        Linedef(vertices[0], vertices[2], sidedefs[0]),
        Linedef(vertices[1], vertices[3], sidedefs[0]),
        Linedef(vertices[2], vertices[3], sidedefs[0]),
    ]
    things = [
        Thing(1, 32.0, 32.0),
    ]
    expected = Textmap(
        vertices=vertices,
        sectors=sectors,
        sidedefs=sidedefs,
        linedefs=linedefs,
        things=things
    )

    assert expected == returned
