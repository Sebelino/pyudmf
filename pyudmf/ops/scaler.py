#!/usr/bin/env python3
from copy import deepcopy
from decimal import Decimal

from pyudmf.grammar.tu import Node, Assignment


def scale(ast, factor: float):
    """ Recursively scales the x and y coordinates of every thing and vertex in the AST. """
    if not isinstance(ast, Node) and not isinstance(ast, list):
        return
    if isinstance(ast, Assignment):
        if ast.identifier in {'x', 'y'}:
            ast.value = Decimal("{0:.3f}".format(float(ast.value) * factor))
        if ast.identifier in {'xscalefloor', 'yscalefloor', 'xscaleceiling', 'yscaleceiling'}:
            ast.value = Decimal("{0:.6f}".format(float(ast.value) * factor))
        elif ast.identifier in {'offsetx', 'offsety'}:
            ast.value = int(ast.value * factor)
        return
    for child in ast:
        scale(child, factor)


def scaled(ast: Node, factor: float) -> Node:
    scaled_ast = deepcopy(ast)
    scale(scaled_ast, factor)
    return scaled_ast
