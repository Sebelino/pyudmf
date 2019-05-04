#!/usr/bin/env python3

from typing import AbstractSet, List, Set, Tuple, Optional

from pyudmf.model.cycle import Cycle


class Vertex(object):
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other: "Vertex"):
        return Vertex(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vertex"):
        return Vertex(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float):
        return Vertex(other * self.x, other * self.y)

    def __rmul__(self, other: float):
        return self.__mul__(other)

    def __repr__(self):
        return "Vertex({}, {})".format(self.x, self.y)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other, Vertex) and self.x == other.x and self.y == other.y


class Sector(object):
    def __init__(self, heightfloor: int, heightceiling: int, texturefloor: str, textureceiling: str,
                 xscalefloor: float = 1.0, yscalefloor: float = 1.0, xscaleceiling: float = 1.0,
                 yscaleceiling: float = 1.0):
        self.heightfloor = int(heightfloor)
        self.heightceiling = int(heightceiling)
        self.texturefloor = str(texturefloor)
        self.textureceiling = str(textureceiling)
        self.xscalefloor = float(xscalefloor)
        self.yscalefloor = float(yscalefloor)
        self.xscaleceiling = float(xscaleceiling)
        self.yscaleceiling = float(yscaleceiling)

    def __repr__(self):
        return "Sector({}, {}, {}, {})".format(self.heightfloor, self.heightceiling, repr(self.texturefloor),
                                               repr(self.textureceiling))

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other,
                          Sector) and self.heightceiling == other.heightceiling and self.texturefloor == other.texturefloor and self.textureceiling == other.textureceiling


class Sidedef(object):
    def __init__(self, sector: Sector, texturemiddle: str, offsetx: int = 0, offsety: int = 0):
        self.sector = sector
        self.texturemiddle = texturemiddle
        self.offsetx = offsetx
        self.offsety = offsety

    def __repr__(self):
        return "Sidedef({}, {})".format(self.sector, repr(self.texturemiddle))

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other, Sidedef) and self.sector == other.sector and self.texturemiddle == other.texturemiddle


class Linedef(object):
    def __init__(
            self,
            v1: Vertex,
            v2: Vertex,
            sidefront: Optional[Sidedef] = None,
            sideback: Optional[Sidedef] = None,
            blocking: bool = False
    ):
        assert v1 != v2
        self.v1 = v1
        self.v2 = v2
        if sidefront is not None:
            assert isinstance(sidefront, Sidedef)
        self.sidefront = sidefront
        if sideback is not None:
            assert isinstance(sideback, Sidedef)
        self.sideback = sideback
        assert isinstance(blocking, bool)
        self.blocking = blocking

    def __repr__(self):
        args = [self.v1, self.v2]
        if self.sidefront:
            args.append("sidefront={}".format(self.sidefront))
        if self.sideback:
            args.append("sideback={}".format(self.sideback))
        if self.blocking:
            args.append("blocking={}".format(self.blocking))
        s = "Linedef({})".format(", ".join(str(a) for a in args))
        return s

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other,
                          Linedef) and self.v1 == other.v1 and self.v2 == other.v2 and self.sidefront == other.sidefront


class Thing(object):
    def __init__(self, thing_type: int, x: float, y: float):
        self.x = x
        self.y = y
        self.type = thing_type

    def __repr__(self):
        return "Thing({}, {}, {})".format(self.type, self.x, self.y)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other, Thing) and self.x == other.x and self.y == other.y and self.type == other.type


class Textmap(object):
    """
    The contents of a TEXTMAP lump.
    """

    def __init__(
            self,
            namespace="zdoom",
            vertices: AbstractSet[Vertex] = frozenset(),
            sidedefs: AbstractSet[Sidedef] = frozenset(),
            linedefs: AbstractSet[Linedef] = frozenset(),
            sectors: AbstractSet[Sector] = frozenset(),
            things: Tuple[Thing] = tuple(),
    ):
        self.namespace = namespace
        self.vertices = frozenset(vertices)
        self.sidedefs = frozenset(sidedefs)
        self.linedefs = frozenset(linedefs)
        self.sectors = frozenset(sectors)
        self.things = tuple(things)  # Actually multiset

    @classmethod
    def _find_cycle(cls, linedef_sets: List[Set[Linedef]], cycles: List[List[Linedef]]):
        """
        :return: Any cycle that encloses one sector, or None if no such cycle exists.
        """
        next_linedef_sets = []
        next_cycles = []
        for i, linedefs in enumerate(linedef_sets):
            if not linedefs:
                return None
            cycle = cycles[i]
            if not cycle:
                neighbor_linedefs = [next(iter(linedefs))]
            else:
                linedef = cycle[-1]
                neighbor_linedefs = [ld for ld in linedefs if {linedef.v1, linedef.v2}.intersection({ld.v1, ld.v2})]
                neighbor_linedefs = [ld for ld in neighbor_linedefs if cls.degree(ld.v1, frozenset(cycle)) <= 1]
                neighbor_linedefs = [ld for ld in neighbor_linedefs if cls.degree(ld.v2, frozenset(cycle)) <= 1]
            if not neighbor_linedefs:
                continue
            for neighbor in neighbor_linedefs:
                next_linedef_set = linedefs.difference({neighbor})
                next_linedef_sets.append(next_linedef_set)
                next_cycle = cycle + [neighbor]
                next_cycles.append(next_cycle)
        for cycle in next_cycles:
            if len(cycle) >= 3 and cycle[0].v1 in {cycle[-1].v1, cycle[-1].v2}:
                return tuple(cycle)
        return cls._find_cycle(next_linedef_sets, next_cycles)

    @classmethod
    def degree(cls, vertex: Vertex, linedefs: AbstractSet[Linedef]):
        """
        :return: The indegree + outdegree of a vertex in the graph
        """
        out_vertices = {ld for ld in linedefs if ld.v1 == vertex}
        in_vertices = {ld for ld in linedefs if ld.v2 == vertex}
        return len(out_vertices) + len(in_vertices)

    @staticmethod
    def determinant(ax, ay, bx, by, cx, cy):
        return bx * cy - by * cx - ax * cy + ax * by + ay * cx - ay * bx

    @classmethod
    def negatively_orient(cls, cycle):
        ld1 = next(cycle)
        ld2 = next(cycle)
        vertices_ld1 = {ld1.v1, ld1.v2}
        vertices_ld2 = {ld2.v1, ld2.v2}
        b = next(iter(vertices_ld1.intersection(vertices_ld2)))
        a = next(iter(vertices_ld1.difference({b})))
        c = next(iter(vertices_ld2.difference({b})))
        det = cls.determinant(a.x, a.y, b.x, b.y, c.x, c.y)
        if det < 0:
            return cycle
        elif det > 0:
            return reversed(cycle)
        else:
            raise NotImplementedError("Zero determinant -- all three vertices are colinear")

    def cycles(self) -> AbstractSet[Cycle]:
        """
        :return: A set of sequences of linedefs such that each sequence of linedefs encloses a sector.
        """
        cycles = set()
        linedefs = set(self.linedefs)
        while linedefs:
            linedefs = {ld for ld in linedefs if
                        self.degree(ld.v1, linedefs) >= 2 and self.degree(ld.v2, linedefs) >= 2}
            cycle = self._find_cycle([linedefs], [[]])
            if cycle:
                cycles.add(cycle)
                cycle_subset = {ld for ld in cycle if
                                self.degree(ld.v1, linedefs) == 2 or self.degree(ld.v2, linedefs) == 2}
                linedefs = linedefs.difference(cycle_subset)
        cycles = frozenset([Cycle(c) for c in cycles])
        cycles = frozenset([self.negatively_orient(c) for c in cycles])
        return cycles

    def __eq__(self, other):
        return all([
            isinstance(other, Textmap),
            self.vertices == other.vertices,
            self.sidedefs == other.sidedefs,
            self.linedefs == other.linedefs,
            self.sectors == other.sectors,
            self.things == other.things,
        ])

    def __repr__(self):
        return "Textmap(vertices={}, sidedefs={}, linedefs={}, sectors={}, things={})".format(
            self.vertices,
            self.sidedefs,
            self.linedefs,
            self.sectors,
            self.things,
        )
