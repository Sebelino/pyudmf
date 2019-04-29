#!/usr/bin/env python3

from decimal import Decimal

import pytest

from pyudmf.grammar.tu import TranslationUnit, Assignment, Block
from pyudmf.model.cycle import Cycle
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
                Assignment("sidefront", 1),
                Assignment("blocking", True),
            ]),
            Block("linedef", [
                Assignment("v1", 2),
                Assignment("v2", 3),
                Assignment("sidefront", 2),
                Assignment("blocking", True),
            ]),
            Block("linedef", [
                Assignment("v1", 3),
                Assignment("v2", 1),
                Assignment("sidefront", 3),
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
                Assignment("heightceiling", 128),
                Assignment("textureceiling", "CEIL3_3"),
                Assignment("texturefloor", "CEIL3_3"),
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

    def test_textmap2ast(self, textmap, ast):
        visage = SebelinoVisage()
        returned = visage.textmap2ast(textmap)

        str(returned)

        assert len(ast) == len(returned)
        assert [x.identifier for x in ast] == [x.identifier for x in returned]
        for i, p in enumerate(zip(ast.global_expr_list, returned.global_expr_list)):
            e, r = p
            assert e == r, "Element at index {} differed".format(i)
        assert ast.global_expr_list == returned.global_expr_list
        assert ast == returned

    def test_bijection(self, textmap):
        visage = SebelinoVisage()
        returned_textmap = ast2textmap(visage.textmap2ast(textmap))
        assert returned_textmap == textmap

    def test_cycle(self, textmap, linedefs):
        cycles = textmap.cycles()
        expected = {
            Cycle([linedefs[0], linedefs[2], linedefs[3], linedefs[1]]),
        }
        assert cycles == expected


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
                Assignment("x", Decimal('64.000')),
                Assignment("y", Decimal('0.000')),
            ]),
            Block("vertex", [
                Assignment("x", Decimal('128.000')),
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
                Assignment("x", Decimal('128.000')),
                Assignment("y", Decimal('64.000')),
            ]),
            Block("linedef", [
                Assignment("v1", 0),
                Assignment("v2", 3),
                Assignment("sidefront", 0),
                Assignment("blocking", True),
            ]),
            Block("linedef", [
                Assignment("v1", 1),
                Assignment("v2", 0),
                Assignment("sidefront", 1),
                Assignment("blocking", True),
            ]),
            Block("linedef", [
                Assignment("v1", 2),
                Assignment("v2", 1),
                Assignment("sidefront", 2),
                Assignment("blocking", True),
            ]),
            Block("linedef", [
                Assignment("v1", 3),
                Assignment("v2", 4),
                Assignment("sidefront", 3),
                Assignment("blocking", True),
            ]),
            Block("linedef", [
                Assignment("v1", 4),
                Assignment("v2", 1),
                Assignment("sidefront", 4),
                Assignment("sideback", 7),
                Assignment("blocking", True),
            ]),
            Block("linedef", [
                Assignment("v1", 4),
                Assignment("v2", 5),
                Assignment("sidefront", 5),
                Assignment("blocking", True),
            ]),
            Block("linedef", [
                Assignment("v1", 5),
                Assignment("v2", 2),
                Assignment("sidefront", 6),
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
                Assignment("sector", 1),
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
                Assignment("heightceiling", 128),
                Assignment("textureceiling", "CEIL3_3"),
                Assignment("texturefloor", "CEIL3_3"),
            ]),
            Block("sector", [
                Assignment("heightceiling", 128),
                Assignment("textureceiling", "CEIL3_3"),
                Assignment("texturefloor", "CEIL3_3"),
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
        sideback_edges = {
            ((64.0, 64.0), (64.0, 0.0)),
        }
        return [
            Linedef(
                Vertex(*v1),
                Vertex(*v2),
                sidefront=sidedefs[0],
                sideback=sidedefs[0] if (v1, v2) in sideback_edges else None,
                blocking=True
            ) for v1, v2 in edges
        ]

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

    def test_cycle(self, textmap, linedefs):
        cycles = textmap.cycles()
        expected = {
            Cycle([linedefs[0], linedefs[1], linedefs[2], linedefs[3]]),
            Cycle([linedefs[4], linedefs[5], linedefs[6], linedefs[2]]),
        }
        assert cycles == expected

    def test_ast2textmap(self, ast, textmap):
        returned = ast2textmap(ast)

        assert textmap == returned

    def test_textmap2ast(self, textmap, ast):
        visage = SebelinoVisage()
        returned = visage.textmap2ast(textmap)

        assert [x for x in ast if x.identifier == "thing"] == [x for x in returned if x.identifier == "thing"]
        assert [x for x in ast if x.identifier == "vertex"] == [x for x in returned if x.identifier == "vertex"]
        assert [x for x in ast if x.identifier == "linedef"] == [x for x in returned if x.identifier == "linedef"]
        assert [x for x in ast if x.identifier == "sidedef"] == [x for x in returned if x.identifier == "sidedef"]
        assert [x for x in ast if x.identifier == "sector"] == [x for x in returned if x.identifier == "sector"]
        assert ast == returned

    def test_bijection(self, textmap):
        visage = SebelinoVisage()
        returned_textmap = ast2textmap(visage.textmap2ast(textmap))
        assert returned_textmap == textmap


class TestTwoByTwoSector(object):
    @pytest.fixture
    def sectors(self):
        return [
            Sector(0, 128, 'MFLR8_1', 'MFLR8_1'),
        ]

    @pytest.fixture
    def sidedefs(self, sectors):
        return [
            Sidedef(sectors[0], 'STONE2'),
        ]

    @pytest.fixture
    def linedefs(self, sidedefs):
        edges = [
            ((128.0, 0.0), (64.0, 0.0)),
            ((0.0, 128.0), (64.0, 128.0)),
            ((0.0, 64.0), (64.0, 64.0)),
            ((64.0, 128.0), (128.0, 128.0)),
            ((64.0, 64.0), (128.0, 64.0)),
            ((64.0, 128.0), (64.0, 64.0)),
            ((64.0, 0.0), (0.0, 0.0)),
            ((128.0, 128.0), (128.0, 64.0)),
            ((0.0, 64.0), (0.0, 128.0)),
            ((128.0, 64.0), (128.0, 0.0)),
            ((64.0, 64.0), (64.0, 0.0)),
            ((0.0, 0.0), (0.0, 64.0)),
        ]
        return [Linedef(Vertex(*v1), Vertex(*v2), sidefront=sidedefs[0], blocking=True) for v1, v2 in edges]

    @pytest.fixture
    def vertices(self):
        return [
            Vertex(0.0, 0.0),
            Vertex(64.0, 0.0),
            Vertex(64.0, 64.0),
            Vertex(0.0, 64.0),
            Vertex(128.0, 64.0),
            Vertex(0.0, 128.0),
            Vertex(128.0, 128.0),
            Vertex(64.0, 128.0),
            Vertex(128.0, 0.0),
        ]

    @pytest.fixture
    def textmap(self, sectors, linedefs, vertices):
        return Textmap(
            namespace="zdoom",
            vertices=frozenset(vertices),
            sidedefs=frozenset({Sidedef(Sector(0, 128, 'MFLR8_1', 'MFLR8_1'), 'STONE2')}),
            linedefs=frozenset(linedefs),
            sectors=frozenset(sectors),
            things=(Thing(1, 32.0, 32.0),))
