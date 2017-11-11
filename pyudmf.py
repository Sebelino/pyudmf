#!/usr/bin/env python

import sys
from copy import deepcopy

from parser import Node, Assignment, parse_udmf


def scale(ast, factor: float):
    """ Recursively scales the x and y coordinates of every thing and vertex in the AST. """
    if not isinstance(ast, Node) and not isinstance(ast, list):
        return
    if isinstance(ast, Assignment):
        if ast.identifier in {'x', 'y'}:
            product = ast.value * factor
            ast.value = int(product) if product == int(product) else product
        return
    for child in ast:
        scale(child, factor)


def scaled(ast: Node, factor: float) -> Node:
    scaled_ast = deepcopy(ast)
    scale(scaled_ast, factor)
    return scaled_ast


if __name__ == '__main__':
    path = sys.argv[1]
    scaling_factor = float(sys.argv[2])
    with open(path, 'r') as f:
        textmap_string = f.read().strip()
    textmap = parse_udmf(textmap_string)
    scale(textmap, scaling_factor)
    print(textmap)
