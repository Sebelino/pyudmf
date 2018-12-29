#!/usr/bin/env python3

from decimal import Decimal
from typing import Dict, List

from pyudmf.grammar.tu import TranslationUnit, Block, Assignment
from pyudmf.model.textmap import Textmap, Vertex, Linedef, Sidedef, Sector, Thing


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


def ast2textmap(tu: TranslationUnit) -> Textmap:
    sectors = [block2sector(e) for e in tu if e.identifier == "sector"]
    things = sorted(block2thing(e) for e in tu if e.identifier == "thing")
    vertices = [block2vertex(e) for e in tu if e.identifier == "vertex"]

    sidedefs = [block2sidedef(e, sectors) for e in tu if e.identifier == "sidedef"]

    linedefs = [block2linedef(e, vertices, sidedefs) for e in tu if e.identifier == "linedef"]

    return Textmap(
        vertices=set(vertices),
        linedefs=set(linedefs),
        sidedefs=set(sidedefs),
        sectors=set(sectors),
        things=things,
    )


# TODO use context
def textmap2ast(textmap: Textmap, context=None) -> TranslationUnit:
    if context is None:
        context = dict(
            vertex_ids={vertex: id for id, vertex in enumerate(textmap.vertices)},
            sidefront_ids={sidefront: id for id, sidefront in enumerate(textmap.sidedefs)},
            sector_ids={sector: id for id, sector in enumerate(textmap.sectors)},
        )

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
        Assignment("sector", context['sector_ids'][sd.sector]),
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
        Assignment("v1", context['vertex_ids'][ld.v1]),
        Assignment("v2", context['vertex_ids'][ld.v2]),
        Assignment("sidefront", context['sidefront_ids'][ld.sidefront]),
        Assignment("blocking", ld.blocking),
    ]) for ld in textmap.linedefs]

    return TranslationUnit(*(header + things + vertices + linedefs + sidedefs + sectors))
