#!/usr/bin/env python3

import itertools
from abc import abstractmethod, ABCMeta
from collections import OrderedDict
from decimal import Decimal
from typing import Dict, Optional, Union

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

        sidedefs = {
            sd: (i, Block("sidedef", [
                Assignment("sector", sectors[sd.sector][0]),
                Assignment("texturemiddle", sd.texturemiddle),
                Assignment("offsetx", sd.offsetx),
                Assignment("offsety", sd.offsety),
            ])) for i, sd in enumerate(textmap.sidedefs)
        }

        vertices = {
            v: (i, Block("vertex", [
                Assignment("x", Decimal("{0:.3f}".format(v.x))),
                Assignment("y", Decimal("{0:.3f}".format(v.y))),
            ])) for i, v in enumerate(textmap.vertices)
        }

        linedefs = {
            ld: Block("linedef", [
                Assignment("v1", vertices[ld.v1][0]),
                Assignment("v2", vertices[ld.v2][0]),
                Assignment("sidefront", sidedefs[ld.sidefront][0]),
                Assignment("blocking", ld.blocking),
            ]) for ld in textmap.linedefs
        }

        things = {
            t: Block("thing", [
                Assignment("x", Decimal("{0:.3f}".format(t.x))),
                Assignment("y", Decimal("{0:.3f}".format(t.y))),
                Assignment("type", t.type),
            ]) for t in textmap.things
        }

        global_exprs = assignments + list(things.values()) + [b for _, b in vertices.values()] + list(linedefs.values()) + [b for _, b in sidedefs.values()] + [b for _, b in sectors.values()]

        assert not any(e is None for e in global_exprs)

        return TranslationUnit(*global_exprs)

    def global_index(self, entity: Union[Vertex, Sector, Sidedef, Linedef, Thing]):
        d = {
            Vertex: self._vertices,
            Sector: self._sectors,
            Sidedef: self._sidedefs,
            Linedef: self._linedefs,
            Thing: self._things,
        }
        entities = d[type(entity)]
        return entities[entity]['global_index']

    def global_namespace_index(self) -> int:
        return self._namespace['global_index']
