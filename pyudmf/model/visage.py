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


class SladeVisage(Visage):
    def textmap2ast(self, textmap: Textmap) -> TranslationUnit:
        assignments = [
            Assignment("namespace", textmap.namespace),
        ]

        sectors = {
            s: (i, Block("sector", [
                Assignment("heightfloor", s.heightfloor),
                Assignment("heightceiling", s.heightceiling),
                Assignment("xscalefloor", Decimal("{0:.6f}".format(s.xscalefloor))),
                Assignment("yscalefloor", Decimal("{0:.6f}".format(s.yscalefloor))),
                Assignment("xscaleceiling", Decimal("{0:.6f}".format(s.xscaleceiling))),
                Assignment("yscaleceiling", Decimal("{0:.6f}".format(s.yscaleceiling))),
                Assignment("texturefloor", s.texturefloor),
                Assignment("textureceiling", s.textureceiling),
            ])) for i, s in enumerate(textmap.sectors)
        }

        ld2sd = {
            ld: (i, ld.sidefront) for i, ld in enumerate(textmap.linedefs)
        }

        sidedefs = [
            (i, Block("sidedef", [
                Assignment("sector", sectors[sd.sector][0]),
                Assignment("texturemiddle", sd.texturemiddle),
                Assignment("offsetx", sd.offsetx),
                Assignment("offsety", sd.offsety),
            ])) for i, sd in ld2sd.values()
        ]
        sidedefs = [b for i, b in sorted(sidedefs, key=lambda k: k[0])]

        vertices = {
            v: (i, Block("vertex", [
                Assignment("x", Decimal("{0:.3f}".format(v.x))),
                Assignment("y", Decimal("{0:.3f}".format(v.y))),
            ])) for i, v in enumerate(textmap.vertices)
        }

        linedefs = [
            Block("linedef", [
                Assignment("v1", vertices[ld.v1][0]),
                Assignment("v2", vertices[ld.v2][0]),
                Assignment("sidefront", ld2sd[ld][0]),
                Assignment("blocking", ld.blocking),
            ]) for ld in textmap.linedefs
        ]

        # TODO multiplicity
        things = {
            t: Block("thing", [
                Assignment("x", Decimal("{0:.3f}".format(t.x))),
                Assignment("y", Decimal("{0:.3f}".format(t.y))),
                Assignment("type", t.type),
            ]) for t in textmap.things
        }

        global_exprs = assignments + list(things.values()) + [b for _, b in vertices.values()] + linedefs + sidedefs + [b for _, b in sectors.values()]

        assert not any(e is None for e in global_exprs)

        return TranslationUnit(*global_exprs)
