#!/usr/bin/env python3

from typing import AbstractSet, List, Set, Tuple

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
    def __init__(self, v1: Vertex, v2: Vertex, sidefront: Sidedef, blocking=False):
        assert v1 != v2
        self.v1 = v1
        self.v2 = v2
        self.sidefront = sidefront
        self.blocking = blocking

    def __repr__(self):
        return "Linedef({}, {}, {})".format(self.v1, self.v2, self.sidefront)

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
            things: List[Thing] = tuple(),
    ):
        self.namespace = namespace
        self.vertices = frozenset(vertices)
        self.sidedefs = frozenset(sidedefs)
        self.linedefs = frozenset(linedefs)
        self.sectors = frozenset(sectors)
        self.things = tuple(things)  # Actually multiset

    @classmethod
    def _find_cycles(cls, linedef_sets: [AbstractSet[Linedef]], cycles: List[List[Linedef]]):
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
                neighbor_linedefs = [ld for ld in linedefs if linedef.v2 in {ld.v1, ld.v2}]
            if not neighbor_linedefs:
                continue
            for neighbor in neighbor_linedefs:
                next_linedef_set = linedefs.difference({neighbor})
                next_linedef_sets.append(next_linedef_set)
                next_cycle = cycle + [neighbor]
                next_cycles.append(next_cycle)
        for cycle in next_cycles:
            if len(cycle) >= 2 and cycle[-1].v2 == cycle[0].v1:
                return tuple(cycle)
        return cls._find_cycles(next_linedef_sets, next_cycles)

    def cycles(self) -> AbstractSet[Cycle]:
        """
        :return: A set of sequences of linedefs such that each sequence of linedefs encloses a sector.
        """
        cycles = set()
        linedefs = set(self.linedefs)
        while linedefs:
            cycle = self._find_cycles([linedefs], [[]])
            if cycle:
                cycles.add(cycle)
                linedefs = linedefs.difference(set(cycle))
        return frozenset([Cycle(c) for c in cycles])

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
