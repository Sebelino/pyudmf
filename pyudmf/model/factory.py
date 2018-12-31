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
    d = {
        'namespace': dict(),
        'things': dict(),
        'sectors': dict(),
        'vertices': dict(),
        'sidedefs': dict(),
        'linedefs': dict(),
    }

    vertices = []
    sectors = []
    things = []

    for i, global_expr in enumerate(tu):
        if isinstance(global_expr, Assignment) and global_expr.identifier == "namespace":
            assert global_expr.value == "zdoom"
            d['namespace']['global_index'] = i
        elif global_expr.identifier == "sector":
            sector = block2sector(global_expr)
            sectors.append(sector)
            d['sectors'][sector] = {'global_index': i}
        elif global_expr.identifier == "thing":
            thing = block2thing(global_expr)
            things.append(thing)
            d['things'][thing] = {'global_index': i}
        elif global_expr.identifier == "vertex":
            vertex = block2vertex(global_expr)
            vertices.append(vertex)
            d['vertices'][vertex] = {'global_index': i}

    sidedefs = []

    for i, global_expr in enumerate(tu):
        if isinstance(global_expr, Assignment) and global_expr.identifier == "namespace":
            pass
        elif global_expr.identifier == "sidedef":
            sidedef = block2sidedef(global_expr, sectors)
            sidedefs.append(sidedef)
            d['sidedefs'][sidedef] = {'global_index': i}

    linedefs = []

    for i, global_expr in enumerate(tu):
        if isinstance(global_expr, Assignment) and global_expr.identifier == "namespace":
            pass
        elif global_expr.identifier == "linedef":
            linedef = block2linedef(global_expr, vertices, sidedefs)
            linedefs.append(linedef)
            d['linedefs'][linedef] = {'global_index': i}

    textmap = Textmap(
        vertices=set(vertices),
        linedefs=set(linedefs),
        sidedefs=set(sidedefs),
        sectors=set(sectors),
        things=things,
    )

    visage = Visage(textmap, d)

    return textmap, visage


def textmap2ast(textmap: Textmap, visage: Optional[Visage] = None) -> TranslationUnit:
    if visage is None:
        visage = Visage(textmap)

    assignments = [
        Assignment("namespace", textmap.namespace),
    ]

    things = {
        t: Block("thing", [
            Assignment("x", Decimal("{0:.3f}".format(t.x))),
            Assignment("y", Decimal("{0:.3f}".format(t.y))),
            Assignment("type", t.type),
        ]) for t in textmap.things
    }

    vertices = {
        v: Block("vertex", [
            Assignment("x", Decimal("{0:.3f}".format(v.x))),
            Assignment("y", Decimal("{0:.3f}".format(v.y))),
        ]) for v in textmap.vertices
    }

    sidedefs = {
        sd: Block("sidedef", [
            Assignment("sector", visage.sector_id(sd.sector)),
            Assignment("texturemiddle", sd.texturemiddle),
            Assignment("offsetx", sd.offsetx),
            Assignment("offsety", sd.offsety),
        ]) for sd in textmap.sidedefs
    }

    sectors = {
        s: Block("sector", [
            Assignment("heightfloor", s.heightfloor),
            Assignment("heightceiling", s.heightceiling),
            Assignment("xscalefloor", Decimal("{0:.6f}".format(s.xscalefloor))),
            Assignment("yscalefloor", Decimal("{0:.6f}".format(s.yscalefloor))),
            Assignment("xscaleceiling", Decimal("{0:.6f}".format(s.xscaleceiling))),
            Assignment("yscaleceiling", Decimal("{0:.6f}".format(s.yscaleceiling))),
            Assignment("texturefloor", s.texturefloor),
            Assignment("textureceiling", s.textureceiling),
        ]) for s in textmap.sectors
    }

    linedefs = {
        ld: Block("linedef", [
            Assignment("v1", visage.vertex_id(ld.v1)),
            Assignment("v2", visage.vertex_id(ld.v2)),
            Assignment("sidefront", visage.sidedef_id(ld.sidefront)),
            Assignment("blocking", ld.blocking),
        ]) for ld in textmap.linedefs
    }

    global_exprs = [None] * sum(len(lst) for lst in (assignments, things, vertices, sectors, sidedefs, linedefs))
    for v in textmap.vertices:
        global_exprs[visage.global_index(v)] = vertices[v]
    for s in textmap.sectors:
        global_exprs[visage.global_index(s)] = sectors[s]
    for sd in textmap.sidedefs:
        global_exprs[visage.global_index(sd)] = sidedefs[sd]
    for ld in textmap.linedefs:
        global_exprs[visage.global_index(ld)] = linedefs[ld]
    for t in textmap.things:
        global_exprs[visage.global_index(t)] = things[t]
    global_exprs[0] = assignments[0]  # TODO

    assert not any(e is None for e in global_exprs)

    return TranslationUnit(*global_exprs)
