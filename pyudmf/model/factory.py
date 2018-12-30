#!/usr/bin/env python3

from decimal import Decimal
from typing import Dict, List, Optional

from pyudmf.grammar.tu import TranslationUnit, Block, Assignment
from pyudmf.model.textmap import Textmap, Vertex, Linedef, Sidedef, Sector, Thing
from pyudmf.model.visage import Visage


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
    d = dict()
    d['sectors'] = []
    d['things'] = []
    d['vertices'] = []
    d['sidedefs'] = []
    d['linedef'] = []

    for i, global_expr in enumerate(tu):
        if not isinstance(global_expr, Block):
            continue
        d[global_expr] = dict()
        d[global_expr]['global_index'] = i
        if global_expr.identifier == "sector":
            d[global_expr]['model'] = block2sector(global_expr)
            d['sectors'].append(d[global_expr]['model'])
        elif global_expr.identifier == "thing":
            d[global_expr]['model'] = block2thing(global_expr)
            d['things'].append(d[global_expr]['model'])
        elif global_expr.identifier == "vertex":
            d[global_expr]['model'] = block2vertex(global_expr)
            d['vertices'].append(d[global_expr]['model'])

    for i, global_expr in enumerate(tu):
        if not isinstance(global_expr, Block):
            continue
        if global_expr.identifier == "sidedef":
            d[global_expr]['model'] = block2sidedef(global_expr, d['sectors'])
            d['sidedefs'].append(d[global_expr]['model'])

    for i, global_expr in enumerate(tu):
        if not isinstance(global_expr, Block):
            continue
        if global_expr.identifier == "linedef":
            d[global_expr]['model'] = block2linedef(global_expr, d['vertices'], d['sidedefs'])
            d['linedef'].append(d[global_expr]['model'])

    sectors = [block2sector(e) for e in tu if e.identifier == "sector"]
    things = sorted(block2thing(e) for e in tu if e.identifier == "thing")
    vertices = [block2vertex(e) for e in tu if e.identifier == "vertex"]

    sidedefs = [block2sidedef(e, sectors) for e in tu if e.identifier == "sidedef"]

    linedefs = [block2linedef(e, vertices, sidedefs) for e in tu if e.identifier == "linedef"]

    textmap = Textmap(
        vertices=set(vertices),
        linedefs=set(linedefs),
        sidedefs=set(sidedefs),
        sectors=set(sectors),
        things=things,
    )

    visage = Visage(textmap, tu)

    return textmap, visage


def textmap2ast(textmap: Textmap, visage: Optional[Visage] = None) -> TranslationUnit:
    if visage is None:
        visage = Visage(textmap)

    header = [
        Assignment("namespace", textmap.namespace),
    ]

    things = [Block("thing", [
        Assignment("x", Decimal("{0:.3f}".format(t.x))),
        Assignment("y", Decimal("{0:.3f}".format(t.y))),
        Assignment("type", t.type),
    ]) for t in textmap.things]

    vertices = [Block("vertex", [
        Assignment("x", Decimal("{0:.3f}".format(v.x))),
        Assignment("y", Decimal("{0:.3f}".format(v.y))),
    ]) for v in textmap.vertices]

    sidedefs = [Block("sidedef", [
        Assignment("sector", visage.sector_id(sd.sector)),
        Assignment("texturemiddle", sd.texturemiddle),
        Assignment("offsetx", sd.offsetx),
        Assignment("offsety", sd.offsety),
    ]) for sd in textmap.sidedefs]

    sectors = [Block("sector", [
        Assignment("heightfloor", s.heightfloor),
        Assignment("heightceiling", s.heightceiling),
        Assignment("xscalefloor", Decimal("{0:.6f}".format(s.xscalefloor))),
        Assignment("yscalefloor", Decimal("{0:.6f}".format(s.yscalefloor))),
        Assignment("xscaleceiling", Decimal("{0:.6f}".format(s.xscaleceiling))),
        Assignment("yscaleceiling", Decimal("{0:.6f}".format(s.yscaleceiling))),
        Assignment("texturefloor", s.texturefloor),
        Assignment("textureceiling", s.textureceiling),
    ]) for s in textmap.sectors]

    linedefs = [Block("linedef", [
        Assignment("v1", visage.vertex_id(ld.v1)),
        Assignment("v2", visage.vertex_id(ld.v2)),
        Assignment("sidefront", visage.sidedef_id(ld.sidefront)),
        Assignment("blocking", ld.blocking),
    ]) for ld in textmap.linedefs]

    return TranslationUnit(*(header + things + vertices + linedefs + sidedefs + sectors))
