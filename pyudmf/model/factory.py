#!/usr/bin/env python3

from pyudmf.grammar.tu import TranslationUnit, Block
from pyudmf.model.textmap import Textmap, Vertex


def ast2textmap(tu: TranslationUnit):
    vertices = set()
    for global_expr in tu:
        if isinstance(global_expr, Block):
            if global_expr.identifier == "vertex":
                xs = [ass.value for ass in global_expr.expressions if ass.identifier == "x"]
                ys = [ass.value for ass in global_expr.expressions if ass.identifier == "y"]
                assert len(xs) == 1
                assert len(ys) == 1
                vertex = Vertex(xs[0], ys[0])
                vertices.add(vertex)
    return Textmap(vertices=vertices)

