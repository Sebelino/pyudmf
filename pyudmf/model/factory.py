#!/usr/bin/env python3

from decimal import Decimal
from typing import Dict, List, Optional

from pyudmf.grammar.tu import TranslationUnit, Block, Assignment
from pyudmf.model.textmap import Textmap, Vertex, Linedef, Sidedef, Sector, Thing
from pyudmf.model.visage import Visage, SebelinoVisage


def block2sector(block: Block):
    props = dict()
    for assignment in block.expressions:
        assert isinstance(assignment, Assignment)
        assert assignment.identifier not in props  # A property shouldn't be set twice within a block
        props[assignment.identifier] = assignment.value
    return Sector(
        props['heightfloor'] if 'heightfloor' in props else 0,
        props['heightceiling'],
        props['texturefloor'],
        props['textureceiling'],
        **{k: v for k, v in props.items() if k in {
            'xscalefloor',
            'yscalefloor',
            'xscaleceiling',
            'yscaleceiling',
        }}
    )


def block2vertex(block: Block):
    props = dict()
    for assignment in block.expressions:
        assert isinstance(assignment, Assignment)
        assert assignment.identifier not in props  # A property shouldn't be set twice within a block
        props[assignment.identifier] = assignment.value
    return Vertex(float(props['x']), float(props['y']))


def block2linedef(block: Block, vertices: List[Vertex], sidedefs: List[Sidedef]):
    props = dict()
    for assignment in block.expressions:
        assert isinstance(assignment, Assignment)
        assert assignment.identifier not in props  # A property shouldn't be set twice within a block
        props[assignment.identifier] = assignment.value
    v1 = vertices[props['v1']]
    v2 = vertices[props['v2']]
    sidefront = sidedefs[props['sidefront']]
    return Linedef(v1, v2, sidefront, props['blocking'])


def block2sidedef(block: Block, sectors: List[Sector]):
    props = dict()
    for assignment in block.expressions:
        assert isinstance(assignment, Assignment)
        assert assignment.identifier not in props  # A property shouldn't be set twice within a block
        props[assignment.identifier] = assignment.value
    sector = sectors[props['sector']]
    return Sidedef(
        sector,
        props['texturemiddle'],
        **{k: v for k, v in props.items() if k in {
            'offsetx',
            'offsety',
        }}
    )


def block2thing(block: Block):
    props = dict()
    for assignment in block.expressions:
        assert isinstance(assignment, Assignment)
        assert assignment.identifier not in props  # A property shouldn't be set twice within a block
        props[assignment.identifier] = assignment.value
    return Thing(props['type'], float(props['x']), float(props['y']))


def ast2textmap(tu: TranslationUnit) -> (Textmap, Dict):
    vertices = []
    sectors = []
    things = []

    for i, global_expr in enumerate(tu):
        if isinstance(global_expr, Assignment) and global_expr.identifier == "namespace":
            assert global_expr.value == "zdoom"
        elif global_expr.identifier == "sector":
            sector = block2sector(global_expr)
            sectors.append(sector)
        elif global_expr.identifier == "thing":
            thing = block2thing(global_expr)
            things.append(thing)
        elif global_expr.identifier == "vertex":
            vertex = block2vertex(global_expr)
            vertices.append(vertex)

    sidedefs = []

    for i, global_expr in enumerate(tu):
        if isinstance(global_expr, Assignment) and global_expr.identifier == "namespace":
            pass
        elif global_expr.identifier == "sidedef":
            sidedef = block2sidedef(global_expr, sectors)
            sidedefs.append(sidedef)

    linedefs = []

    for i, global_expr in enumerate(tu):
        if isinstance(global_expr, Assignment) and global_expr.identifier == "namespace":
            pass
        elif global_expr.identifier == "linedef":
            linedef = block2linedef(global_expr, vertices, sidedefs)
            linedefs.append(linedef)

    textmap = Textmap(
        vertices=set(vertices),
        linedefs=set(linedefs),
        sidedefs=set(sidedefs),
        sectors=set(sectors),
        things=things,
    )

    return textmap


def textmap2ast(textmap: Textmap):
    visage = SebelinoVisage()
    return visage.textmap2ast(textmap)
