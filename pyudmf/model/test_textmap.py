#!/usr/bin/env python3

from decimal import Decimal

import pytest

from pyudmf.grammar.tu import TranslationUnit, Assignment, Block
from pyudmf.model.factory import ast2textmap
from pyudmf.model.textmap import Textmap, Vertex, Linedef, Sector, Sidedef, Thing
from pyudmf.model.visage import SebelinoVisage


@pytest.fixture
def things():
    return [
        Thing(1, 32.0, 32.0),
    ]


class TestMonosector(object):
    @pytest.fixture
    def ast(self) -> TranslationUnit:
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
                Assignment("x", Decimal('64.000')),
                Assignment("y", Decimal('0.000')),
            ]),
            Block("vertex", [
                Assignment("x", Decimal('0.000')),
                Assignment("y", Decimal('64.000')),
            ]),
            Block("vertex", [
                Assignment("x", Decimal('64.000')),
                Assignment("y", Decimal('64.000')),
            ]),
            Block("linedef", [
                Assignment("v1", 0),
                Assignment("v2", 2),
                Assignment("sidefront", 0),
                Assignment("blocking", True),
            ]),
            Block("linedef", [
                Assignment("v1", 1),
                Assignment("v2", 0),
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
                Assignment("v2", 1),
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
    def vertices(self):
        return [
            Vertex(0.0, 0.0),
            Vertex(64.0, 0.0),
            Vertex(0.0, 64.0),
            Vertex(64.0, 64.0),
        ]

    @pytest.fixture
    def sectors(self):
        return [
            Sector(0, 128, "CEIL3_3", "CEIL3_3"),
        ]

    @pytest.fixture
    def sidedefs(self, sectors):
        return [
            Sidedef(sectors[0], "MARBFACE"),
        ]

    @pytest.fixture
    def linedefs(self, vertices, sidedefs):
        return [
            Linedef(vertices[0], vertices[2], sidedefs[0], blocking=True),
            Linedef(vertices[1], vertices[0], sidedefs[0], blocking=True),
            Linedef(vertices[2], vertices[3], sidedefs[0], blocking=True),
            Linedef(vertices[3], vertices[1], sidedefs[0], blocking=True),
        ]

    @pytest.fixture
    def textmap(self, vertices, sectors, sidedefs, linedefs, things) -> Textmap:
        return Textmap(
            namespace="zdoom",
            vertices=frozenset(vertices),
            sectors=frozenset(sectors),
            sidedefs=frozenset(sidedefs),
            linedefs=frozenset(linedefs),
            things=things
        )

    def test_ast2textmap(self, ast, textmap):
        returned = ast2textmap(ast)

        assert textmap == returned

    @pytest.mark.skip
    def test_textmap2ast(self, textmap, ast):
        visage = SebelinoVisage()
        returned = visage.textmap2ast(textmap)

        str(returned)

        assert len(ast) == len(returned)
        assert [x.identifier for x in ast] == [x.identifier for x in returned]
        for i, p in enumerate(zip(ast.global_expr_list, returned.global_expr_list)):
            e, r = p
            assert e == r, "Element {} differed".format(i)
        assert ast.global_expr_list == returned.global_expr_list
        assert ast == returned

    def test_bijection(self, textmap):
        visage = SebelinoVisage()
        returned_textmap = ast2textmap(visage.textmap2ast(textmap))
        assert returned_textmap == textmap


class TestDuosector(object):
    @pytest.fixture
    def ast(self) -> TranslationUnit:
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
                Assignment("y", Decimal('64.000')),
            ]),
            Block("vertex", [
                Assignment("x", Decimal('64.000')),
                Assignment("y", Decimal('64.000')),
            ]),
            Block("vertex", [
                Assignment("x", Decimal('64.000')),
                Assignment("y", Decimal('0.000')),
            ]),
            Block("vertex", [
                Assignment("x", Decimal('128.000')),
                Assignment("y", Decimal('64.000')),
            ]),
            Block("vertex", [
                Assignment("x", Decimal('128.000')),
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
            Block("linedef", [
                Assignment("v1", 2),
                Assignment("v2", 4),
                Assignment("sidefront", 0),
                Assignment("blocking", True),
            ]),
            Block("linedef", [
                Assignment("v1", 4),
                Assignment("v2", 5),
                Assignment("sidefront", 0),
                Assignment("blocking", True),
            ]),
            Block("linedef", [
                Assignment("v1", 5),
                Assignment("v2", 3),
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
            Block("sidedef", [
                Assignment("sector", 1),
                Assignment("texturemiddle", "MARBFACE"),
            ]),
            Block("sidedef", [
                Assignment("sector", 1),
                Assignment("texturemiddle", "MARBFACE"),
            ]),
            Block("sidedef", [
                Assignment("sector", 1),
                Assignment("texturemiddle", "MARBFACE"),
            ]),
            Block("sector", [
                Assignment("texturefloor", "CEIL3_3"),
                Assignment("textureceiling", "CEIL3_3"),
                Assignment("heightceiling", 128),
            ]),
            Block("sector", [
                Assignment("texturefloor", "CEIL3_3"),
                Assignment("textureceiling", "CEIL3_3"),
                Assignment("heightceiling", 128),
            ]),
        )

    @pytest.fixture
    def sectors(self):
        return [
            Sector(0, 128, "CEIL3_3", "CEIL3_3"),
        ]

    @pytest.fixture
    def sidedefs(self, sectors):
        return [
            Sidedef(sectors[0], "MARBFACE"),
        ]

    @pytest.fixture
    def linedefs(self, sidedefs):
        edges = (
            ((0.0, 0.0), (0.0, 64.0)),
            ((0.0, 64.0), (64.0, 64.0)),
            ((64.0, 64.0), (64.0, 0.0)),
            ((64.0, 0.0), (0.0, 0.0)),
            ((64.0, 64.0), (128.0, 64.0)),
            ((128.0, 64.0), (128.0, 0.0)),
            ((128.0, 0.0), (64.0, 0.0)),
        )
        return [Linedef(Vertex(*v1), Vertex(*v2), sidedefs[0], blocking=True) for v1, v2 in edges]

    @pytest.fixture
    def textmap(self, sectors, sidedefs, linedefs, things) -> Textmap:
        vertices = {ld.v1 for ld in linedefs}.union({ld.v2 for ld in linedefs})
        return Textmap(
            namespace="zdoom",
            vertices=vertices,
            sectors=frozenset(sectors),
            sidedefs=frozenset(sidedefs),
            linedefs=frozenset(linedefs),
            things=things
        )

    def test_ast2textmap(self, ast, textmap):
        returned = ast2textmap(ast)

        assert textmap == returned

    @pytest.mark.skip
    def test_textmap2ast(self, textmap, ast):
        visage = SebelinoVisage()
        returned = visage.textmap2ast(textmap)

        str(returned)

        assert len(ast) == len(returned)
        assert [x.identifier for x in ast] == [x.identifier for x in returned]

    def test_bijection(self, textmap):
        visage = SebelinoVisage()
        returned_textmap = ast2textmap(visage.textmap2ast(textmap))
        assert returned_textmap == textmap
