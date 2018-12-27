#!/usr/bin/env python
import argparse
from copy import deepcopy

from pyudmf.parser import Node, Assignment, parse_udmf


def scale(ast, factor: float):
    """ Recursively scales the x and y coordinates of every thing and vertex in the AST. """
    if not isinstance(ast, Node) and not isinstance(ast, list):
        return
    if isinstance(ast, Assignment):
        if ast.identifier in {'x', 'y', 'xscalefloor', 'yscalefloor', 'xscaleceiling', 'yscaleceiling'}:
            product = float(ast.value * factor)
            ast.value = product
        elif ast.identifier in {'offsetx', 'offsety'}:
            product = int(ast.value * factor)
            ast.value = product
        return
    for child in ast:
        scale(child, factor)


def scaled(ast: Node, factor: float) -> Node:
    scaled_ast = deepcopy(ast)
    scale(scaled_ast, factor)
    return scaled_ast


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scale an UDMF formatted Doom map.")
    parser.add_argument('infile', help="Path to the TEXTMAP lump file.")
    parser.add_argument('scalingfactor', type=float, help="Scaling factor. E.g. if the factor is 0.5, the map will"
                                                          " shrink to 25 %% of its original area.")

    args = parser.parse_args()

    with open(args.infile, 'r') as f:
        textmap_string = f.read().strip()
    textmap = parse_udmf(textmap_string)
    scale(textmap, args.scalingfactor)
    print(textmap)
