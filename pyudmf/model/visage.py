#!/usr/bin/env python3

from abc import abstractmethod, ABCMeta
from decimal import Decimal
from typing import Tuple, Dict, Any

from pyudmf.grammar.tu import TranslationUnit, Assignment, Block
from pyudmf.model.cycle import Cycle
from pyudmf.model.textmap import Textmap, Sector, Sidedef


class Visage(metaclass=ABCMeta):
    """
    Represents a specific way to encode a UDMF map as a TEXTMAP lump.
    """

    @abstractmethod
    def textmap2ast(self, textmap: Textmap) -> TranslationUnit:
        raise NotImplementedError


class SebelinoVisage(Visage):
    """
    Layout:

    Assignments
    Things
    Vertices
    Linedefs
    Sidedefs
    Sectors

    Things are sorted primarily by y, secondarily by x, ascending order.
    Vertices are sorted primarily by y, secondarily by x, ascending order.
    Linedefs are sorted primarily by v1 index, secondarily by v2 index, ascending order.
    Sidedefs are sorted by sector index, ascending order.
    Assignments within Sectors are sorted alphabetically, ascending order.
    """

    @staticmethod
    def _linedef_orientation(cycle: Cycle):
        sidefronts = set()
        sidebacks = set()
        for _ in range((len(cycle) + 1) // 2):
            ld1 = next(cycle)
            ld2 = next(cycle)
            if ld1.v1 == ld2.v1:  # Tail-tail
                sidebacks.add(ld1)
                sidefronts.add(ld2)
            elif ld1.v1 == ld2.v2:  # Tail-head
                sidebacks.add(ld1)
                sidebacks.add(ld2)
            elif ld1.v2 == ld2.v1:  # Head-tail
                sidefronts.add(ld1)
                sidefronts.add(ld2)
            elif ld1.v2 == ld2.v2:  # Head-head
                sidefronts.add(ld1)
                sidebacks.add(ld2)
        return frozenset(sidefronts), frozenset(sidebacks)

    def textmap2ast(self, textmap: Textmap) -> TranslationUnit:
        assignments = [
            Assignment("namespace", textmap.namespace),
        ]

        global_exprs = assignments + self._add_things(textmap)

        assert not any(e is None for e in global_exprs)

        return TranslationUnit(*global_exprs)

    def _add_things(self, textmap: Textmap):
        # TODO multiplicity
        things = {
            t: Block("thing", [
                Assignment("x", Decimal("{0:.3f}".format(t.x))),
                Assignment("y", Decimal("{0:.3f}".format(t.y))),
                Assignment("type", t.type),
            ]) for t in textmap.things
        }

        return list(things.values()) + self._add_vertices(textmap)

    def _add_vertices(self, textmap: Textmap):
        vertices = {
            v: Block("vertex", [
                Assignment("x", Decimal("{0:.3f}".format(v.x))),
                Assignment("y", Decimal("{0:.3f}".format(v.y))),
            ]) for i, v in enumerate(sorted(textmap.vertices, key=lambda e: (e.y, e.x)))
        }

        vertex_list = sorted(vertices.items(), key=lambda e: (e[0].y, e[0].x))
        vertex_list = [b for _, b in vertex_list]

        return vertex_list + self._add_linedefs(textmap)

    def _add_linedefs(self, textmap: Textmap):
        vertices = {v: i for i, v in enumerate(sorted(textmap.vertices, key=lambda e: (e.y, e.x)))}

        linedefs = {(vertices[ld.v1], vertices[ld.v2], ld) for ld in textmap.linedefs}

        linedefs = [(v1, v2, sdid, ld) for sdid, (v1, v2, ld) in
                    enumerate(sorted(linedefs, key=lambda e: (e[0], e[1])))]

        cycles = textmap.cycles()

        cycles_sides = {self._linedef_orientation(c) for c in cycles}
        sidebacks = {sb for _, sb in cycles_sides}

        sidedefs = self._to_sidedefs(cycles_sides, [ld for _, _, _, ld in linedefs])

        linedefs = self._add_sidebacks(linedefs, {x for y in sidebacks for x in y})

        linedefs = {
            (vertices[ld.v1], vertices[ld.v2], Block("linedef", self._to_block(sfid, sbid, ld, vertices))) for
            v1, v2, (sfid, sbid), ld in linedefs
        }

        linedef_list = [b for _, _, b in sorted(linedefs, key=lambda e: (e[0], e[1]))]

        return linedef_list + self._add_sidedefs(textmap, sidedefs, cycles_sides)

    def _add_sidedefs(self, textmap: Textmap, sidedefs, cycles_sides):
        return sidedefs + self._add_sectors(textmap, cycles_sides)

    def _add_sectors(self, textmap: Textmap, cycles_sides):

        sector_list = [Block("sector", self._s2blocklist(s)) for s in textmap.sectors]
        sector_list *= len(cycles_sides)

        return sector_list

    @classmethod
    def _s2blocklist(cls, s: Sector):
        blocklist = [
            Assignment("heightceiling", s.heightceiling),
            Assignment("texturefloor", s.texturefloor),
            Assignment("textureceiling", s.textureceiling),
        ]
        if s.heightfloor:
            blocklist.append(Assignment("heightfloor", s.heightfloor))
        if s.xscalefloor != 1.0:
            blocklist.append(Assignment("xscalefloor", Decimal("{0:.6f}".format(s.xscalefloor))))
        if s.yscalefloor != 1.0:
            blocklist.append(Assignment("yscalefloor", Decimal("{0:.6f}".format(s.yscalefloor))))
        if s.xscaleceiling != 1.0:
            blocklist.append(Assignment("xscaleceiling", Decimal("{0:.6f}".format(s.xscaleceiling))))
        if s.yscaleceiling != 1.0:
            blocklist.append(Assignment("yscaleceiling", Decimal("{0:.6f}".format(s.yscaleceiling))))
        return list(sorted(blocklist, key=lambda a: a.identifier))

    @classmethod
    def _assign_cycle_to_sectorid(cls, linedef_list, cycles) -> Dict[Any, int]:
        cycle_to_sectorid = dict()

        sector_index = 0
        for ld in linedef_list:
            for fcycle, bcycle in cycles:
                if ld in fcycle:
                    if (fcycle, bcycle) not in cycle_to_sectorid.keys():
                        cycle_to_sectorid[(fcycle, bcycle)] = sector_index
                        sector_index += 1
                    break
        return cycle_to_sectorid

    @classmethod
    def _ld2sdid(cls, linedef_list, cycle_to_sectorid: Dict[Any, int]) -> Tuple[int]:
        sectorids = []

        for ld in linedef_list:
            for (fcycle, _), sid in cycle_to_sectorid.items():
                if ld in fcycle:
                    sectorids.append(sid)

        return tuple(sectorids)

    @classmethod
    def _ld2sdid_back(cls, linedef_list, cycle_to_sectorid: Dict[Any, int]) -> Tuple[int]:
        sectorids = []

        for ld in linedef_list:
            for (_, bcycle), sid in cycle_to_sectorid.items():
                if ld in bcycle:
                    sectorids.append(sid)

        return tuple(sectorids)

    @classmethod
    def _to_sidedefs(cls, cycles_sides, linedef_list):
        cycle_to_sectorid = cls._assign_cycle_to_sectorid(linedef_list, cycles_sides)

        front_sector_ids = cls._ld2sdid(linedef_list, cycle_to_sectorid)

        sidefronts = [
            Block("sidedef", [
                Assignment("sector", sector_id),
                Assignment("texturemiddle", "MARBFACE"),
            ])
            for sector_id in front_sector_ids
        ]

        back_sector_ids = cls._ld2sdid_back(linedef_list, cycle_to_sectorid)

        sidebacks = [
            Block("sidedef", [
                Assignment("sector", sector_id),
                Assignment("texturemiddle", "MARBFACE"),
            ])
            for sector_id in back_sector_ids
        ]

        return sidefronts + sidebacks

    @classmethod
    def sd2blocklist(cls, sd: Sidedef, sectors):
        blocklist = [
            Assignment("sector", sectors[sd.sector][0]),
            Assignment("texturemiddle", sd.texturemiddle),
        ]
        if sd.offsetx:
            blocklist.append(Assignment("offsetx", sd.offsetx))
        if sd.offsety:
            blocklist.append(Assignment("offsety", sd.offsety))
        return blocklist

    @classmethod
    def _add_sidebacks(cls, linedefs, sidebacks):
        sorted_linedefs = sorted(linedefs, key=lambda e: (e[0], e[1]))
        new_linedefs = []
        next_sideback_index = len(sorted_linedefs)
        for v1, v2, sidefront_id, ld in sorted_linedefs:
            sideback_id = None
            if ld in sidebacks:
                sideback_id = next_sideback_index
                next_sideback_index += 1
            new_linedefs.append((v1, v2, (sidefront_id, sideback_id), ld))
        return new_linedefs

    @classmethod
    def _to_block(cls, sfid, sbid, ld, vertices):
        lists = []
        lists += [
            Assignment("v1", vertices[ld.v1]),
            Assignment("v2", vertices[ld.v2]),
            Assignment("sidefront", sfid),
        ]
        lists += [] if sbid is None else [Assignment("sideback", sbid)]
        lists += [Assignment("blocking", ld.blocking)]
        return lists
