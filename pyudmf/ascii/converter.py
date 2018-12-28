#!/usr/bin/env python

import sys


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
