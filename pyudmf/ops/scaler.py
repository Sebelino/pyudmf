#!/usr/bin/env python3

from pyudmf.model.textmap import Textmap, Thing, Sector, Sidedef, Vertex


def scaled(textmap: Textmap, factor: float) -> Textmap:
    """ Scales the x and y coordinates of every thing and vertex in the textmap. """

    sectors = {Sector(
        s.heightfloor,
        s.heightceiling,
        s.texturefloor,
        s.textureceiling,
        xscalefloor=factor * s.xscalefloor,
        yscalefloor=factor * s.yscalefloor,
        xscaleceiling=factor * s.xscaleceiling,
        yscaleceiling=factor * s.yscaleceiling,
    ) for s in textmap.sectors}
    sidedefs = {Sidedef(
        sd.texturemiddle,
        factor * sd.offsetx,
        factor * sd.offsety
    ) for sd in textmap.sidedefs}
    vertices = {Vertex(factor * v.x, factor * v.y) for v in textmap.vertices}
    linedefs = textmap.linedefs
    things = [Thing(t.type, factor * t.x, factor * t.y) for t in textmap.things]

    return Textmap(
        vertices=vertices,
        linedefs=linedefs,
        sidedefs=sidedefs,
        sectors=sectors,
        things=things,
    )
