#!/usr/bin/env python3

from abc import abstractmethod, ABCMeta
from decimal import Decimal
from typing import Union

from pyudmf.grammar.tu import TranslationUnit, Assignment, Block
from pyudmf.model.textmap import Textmap, Thing, Vertex, Sector, Sidedef, Linedef


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

    def textmap2ast(self, textmap: Textmap) -> TranslationUnit:
        assignments = [
            Assignment("namespace", textmap.namespace),
        ]

        def s2blocklist(s: Sector):
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

        sectors = {
            s: (i, Block("sector", s2blocklist(s))) for i, s in enumerate(textmap.sectors)
        }

        ld2sd = {
            ld: (i, ld.sidefront) for i, ld in enumerate(textmap.linedefs)
        }

        def sd2blocklist(sd: Sidedef):
            blocklist = [
                Assignment("sector", sectors[sd.sector][0]),
                Assignment("texturemiddle", sd.texturemiddle),
            ]
            if sd.offsetx:
                blocklist.append(Assignment("offsetx", sd.offsetx))
            if sd.offsety:
                blocklist.append(Assignment("offsety", sd.offsety))
            return blocklist

        sidedefs = [
            (i, Block("sidedef", sd2blocklist(sd))) for i, sd in ld2sd.values()
        ]
        sidedefs = [b for i, b in sorted(sidedefs, key=lambda k: k[0])]

        vertices = {
            v: (i, Block("vertex", [
                Assignment("x", Decimal("{0:.3f}".format(v.x))),
                Assignment("y", Decimal("{0:.3f}".format(v.y))),
            ])) for i, v in enumerate(sorted(textmap.vertices, key=lambda e: (e.y, e.x)))
        }

        linedefs = {
            (vertices[ld.v1][0], vertices[ld.v2][0], Block("linedef", [
                Assignment("v1", vertices[ld.v1][0]),
                Assignment("v2", vertices[ld.v2][0]),
                # Assignment("sidefront", ld2sd[ld][0]),
                Assignment("sidefront", 0),
                Assignment("blocking", ld.blocking),
            ])) for ld in textmap.linedefs
        }

        # TODO multiplicity
        things = {
            t: Block("thing", [
                Assignment("x", Decimal("{0:.3f}".format(t.x))),
                Assignment("y", Decimal("{0:.3f}".format(t.y))),
                Assignment("type", t.type),
            ]) for t in textmap.things
        }

        vertex_list = sorted(vertices.items(), key=lambda e: (e[0].y, e[0].x))
        vertex_list = [b for _, (_, b) in vertex_list]

        linedef_list = [b for _, _, b in sorted(linedefs, key=lambda e: (e[0], e[1]))]

        global_exprs = assignments + list(things.values()) + vertex_list + linedef_list + sidedefs + [
            b for _, b in sectors.values()]

        assert not any(e is None for e in global_exprs)

        return TranslationUnit(*global_exprs)
