#!/usr/bin/env python

from typing import AbstractSet, Set, List

from pyudmf.model.textmap import Vertex, Sidedef, Sector, Linedef, Textmap, Thing

xscale = yscale = 64


def _asciimap2vertices(asciimap) -> AbstractSet[Vertex]:
    """ :return A set of points (x, y) such that the character at column x and line y is '.'.  """
    vertices = set()
    for lineno, line in enumerate(asciimap):
        for colno, char in enumerate(line):
            if char == '.':
                x = xscale * colno
                y = yscale * (len(asciimap) - 1 - lineno)
                vbl = Vertex(x, y)
                vtl = Vertex(x, y + yscale)
                vtr = Vertex(x + xscale, y + yscale)
                vbr = Vertex(x + xscale, y)
                vertices.add(vbl)
                vertices.add(vtl)
                vertices.add(vtr)
                vertices.add(vbr)  # I know this is 4 times slower...
            else:
                raise ValueError()
    return vertices


def _asciimap2sectors(asciimap) -> AbstractSet[Sector]:
    return {Sector(0, 128, "MFLR8_1", "MFLR8_1")}


def _sectors2sidedefs(sectors: AbstractSet[Sector]):
    return {Sidedef(s, "STONE2") for s in sectors}


def _neighbors(vertex: Vertex, vertices: Set[Vertex]):
    west = Vertex(vertex.x - xscale, vertex.y)
    east = Vertex(vertex.x + xscale, vertex.y)
    south = Vertex(vertex.x, vertex.y - yscale)
    north = Vertex(vertex.x, vertex.y + yscale)
    return vertices.intersection({west, east, south, north})


def _is_inner_vertex(vertex: Vertex, vertices: Set[Vertex]):
    return len(_neighbors(vertex, vertices)) == 4


def _spanning_vertices(vertices: Set[Vertex]) -> AbstractSet[Vertex]:
    """ :return The subset of vertices such that every vertex is not within any polygon that can
    be constructed from the remaining vertices. """
    # Raycasting should not be necessary here.
    span = set(vertices)
    for v in vertices:
        if _is_inner_vertex(v, vertices):
            span.remove(v)
    return span


def generate_linedefs(vertices: AbstractSet[Vertex], sidedefs: AbstractSet[Sidedef]) -> AbstractSet[Linedef]:
    linedefs = set()
    # vertices = _spanning_vertices(vertices)

    for vertex in sorted(vertices, key=lambda k: (k.y, k.x)):
        east = Vertex(vertex.x + xscale, vertex.y)
        northeast = Vertex(vertex.x + xscale, vertex.y + yscale)
        north = Vertex(vertex.x, vertex.y + yscale)

        if north in vertices and not (north, vertex) in linedefs:
            linedefs.add((vertex, north))
        if north in vertices and northeast in vertices and not (northeast, north) in linedefs:
            linedefs.add((north, northeast))
        if east in vertices and northeast in vertices and not (east, northeast) in linedefs:
            linedefs.add((northeast, east))
        if east in vertices and not (vertex, east) in linedefs:
            linedefs.add((east, vertex))
    return {Linedef(v1, v2, list(sidedefs)[0], blocking=True) for v1, v2 in linedefs}


def asciimap2textmap(asciimap: List[str]) -> Textmap:
    asciimap = [line.strip() for line in asciimap]
    asciimap = [line for line in asciimap if line]
    vertices = _asciimap2vertices(asciimap)
    sectors = _asciimap2sectors(asciimap)
    sidedefs = _sectors2sidedefs(sectors)
    linedefs = generate_linedefs(vertices, sidedefs)
    things = [Thing(1, 0.5 * xscale, 0.5 * yscale)]
    textmap = Textmap(
        vertices=vertices,
        sectors=sectors,
        sidedefs=sidedefs,
        linedefs=linedefs,
        things=things,
    )
    return textmap
