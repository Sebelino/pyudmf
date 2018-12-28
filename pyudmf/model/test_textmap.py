#!/usr/bin/env python3

from decimal import Decimal

from pyudmf.grammar.tu import TranslationUnit, Assignment, Block
from pyudmf.model.factory import ast2textmap
from pyudmf.model.textmap import Textmap, Vertex


def test_textmap():
    tu = TranslationUnit(
        Block("vertex", [
            Assignment("x", Decimal(0.0)),
            Assignment("y", Decimal(0.0)),
        ]),
    )

    returned = ast2textmap(tu)
    expected = Textmap(vertices={Vertex(0.0, 0.0)})

    assert expected == returned
