#!/usr/bin/env python

import sys
from abc import abstractmethod, ABCMeta


class Block(metaclass=ABCMeta):
    def __str__(self):
        raise NotImplementedError()


class Vertex(Block):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Vertex({}, {})".format(self.x, self.y)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other, Vertex) and self.x == other.x and self.y == other.y

    def __str__(self):
        return "vertex {{ x = {0}; y = {1}; }}".format(self.x, self.y)
        #return "vertex {{ x = {0:.3f}; y = {1:.3f}; }}".format(self.x, self.y)


class Sidedef(Block):
    def __init__(self, sectorid, texturemiddle):
        self.sectorid = sectorid
        self.texturemiddle = texturemiddle

    def __repr__(self):
        return "Sidedef({}, {})".format(self.sectorid, self.texturemiddle)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other, Sidedef) and self.sectorid == other.sectorid and self.texturemiddle == other.texturemiddle

    def __str__(self):
        return 'sidedef {{ sector = {0}; texturemiddle = "{1}"; }}'.format(self.sectorid, self.texturemiddle)


class Linedef(Block):
    def __init__(self, v1, v2, sidefront_id):
        self.v1 = v1
        self.v2 = v2
        self.sidefront_id = sidefront_id

    def __repr__(self):
        return "Linedef({}, {}, {})".format(self.v1, self.v2, self.sidefront_id)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other, Linedef) and self.v1 == other.v1 and self.v2 == other.v2 and self.sidefront_id == other.sidefront_id

    def __str__(self):
        return "linedef {{ v1 = {0}; v2 = {1}; sidefront = {2}; blocking = true; }}".format(self.v1, self.v2, self.sidefront_id)
        #return "linedef {{ v1 = {0}; v2 = {1}; sidefront = {2}; blocking = false; }}".format(self.v1, self.v2, self.sidefront_id)


class Sector(Block):
    def __init__(self, heightceiling, texturefloor, textureceiling):
        self.heightceiling = heightceiling
        self.texturefloor = texturefloor
        self.textureceiling = textureceiling

    def __repr__(self):
        return "Sector({}, {}, {})".format(self.heightceiling, self.texturefloor, self.textureceiling)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other, Sector) and self.heightceiling == other.heightceiling and self.texturefloor == other.texturefloor and self.textureceiling == other.textureceiling

    def __str__(self):
        return 'sector {{ heightceiling = {0}; texturefloor = "{1}"; textureceiling = "{2}"; }}'.format(self.heightceiling, self.texturefloor, self.textureceiling)


class Thing(Block):
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "Sector({})".format(self.s)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other, Thing) and self.s == other.s

    def __str__(self):
        return self.s


class Converter(object):
    def __init__(self, asciimap):
        """ @asciimap is a list of strings. """
        self.xscale = self.yscale = 64
        self.sectorcount = "".join(asciimap).count('.')
        self.header = 'namespace = "zdoom";'
        self.vertices = list(self._asciimap2vertices(asciimap))
        self.vertices_dict = {e: i for i, e in enumerate(self.vertices)}  # For faster lookup
        self.sidedefs = list(self._sidedefs())
        self.sidedefs_dict = {e: i for i, e in enumerate(self.sidedefs)}  # For faster lookup
        self.linedefs = self._linedefs()
        self.sectors = self._asciimap2sectors(asciimap)
        self.things = self._things()

    def _asciimap2entries(self, asciimap):
        return set()

    def _asciimap2vertices(self, asciimap):
        """ :return A set of points (x, y) such that the character at column x and line y is '.'.  """
        points = set()
        for lineno, line in enumerate(asciimap):
            for colno, char in enumerate(line):
                if char == '.':
                    x = self.xscale * colno
                    y = self.yscale * (len(asciimap) - 1 - lineno)
                    vbl = Vertex(x, y)
                    vtl = Vertex(x, y + self.yscale)
                    vtr = Vertex(x + self.xscale, y + self.yscale)
                    vbr = Vertex(x + self.xscale, y)
                    points.add(vbl)
                    points.add(vtl)
                    points.add(vtr)
                    points.add(vbr)  # I know this is 4 times slower...
                else:
                    raise ValueError()
        return points

    def _asciimap2sectors(self, asciimap):
        return [Sector(128, "MFLR8_1", "MFLR8_1") for _ in range(self.sectorcount)]

    def _sidedefs(self):
        return {Sidedef(i, "STONE2") for i in range(self.sectorcount)}

    def _neighbor_indices_of(self, vertex, vertices):
        west = Vertex(vertex.x - self.xscale, vertex.y)
        east = Vertex(vertex.x + self.xscale, vertex.y)
        south = Vertex(vertex.x, vertex.y - self.yscale)
        north = Vertex(vertex.x, vertex.y + self.yscale)
        neighbors = set()
        for candidate in {west, east, south, north}:
            if candidate in vertices:
                vertex_index = self.vertices_dict[candidate]
                neighbors.add(vertex_index)
        return neighbors

    def _spanning_vertices(self):
        """ :return The subset of vertices such that every vertex is not within any polygon that can
        be constructed from the remaining vertices. """
        # Raycasting should not be necessary here.
        span = set(self.vertices)
        for v in self.vertices:
            neighbors = self._neighbor_indices_of(v, self.vertices)
            print("{} [{}]: {}".format(repr(v), len(neighbors), {self.vertices[w] for w in neighbors}), file=sys.stderr)
            if len(neighbors) == 4:
                span.remove(v)
        print("span={}".format(span), file=sys.stderr)
        return span


    def _linedefs(self):
        linedefs = set()
        spanningvertices = self._spanning_vertices()
        for v in spanningvertices:
            for v2 in self._neighbor_indices_of(v, spanningvertices):
                v1 = self.vertices_dict[v]
                if Linedef(v2, v1, 0) not in linedefs:
                    linedefs.add(Linedef(v1, v2, 0))  # TODO sidedef
        return linedefs

    def _things(self):
        s = """
thing
{
x = 32.000;
y = 32.000;
type = 1;
coop = true;
dm = true;
single = true;
skill1 = true;
skill2 = true;
skill3 = true;
skill4 = true;
skill5 = true;
}
        """.strip()
        return {s}

    def __str__(self):
        return "\n\n".join([self.header,
                "\n".join(str(t) for t in self.things),
                "\n".join(str(v) for v in self.vertices),
                "\n".join(str(v) for v in self.linedefs),
                "\n".join(str(sd) for sd in self.sidedefs),
                "\n".join(str(s) for s in self.sectors)]).strip()

if __name__ == '__main__':
    path = sys.argv[1]
    with open(path, 'r') as f:
        asciimap = f.read().strip().split('\n')
    converter = Converter(asciimap)
    print(converter)
