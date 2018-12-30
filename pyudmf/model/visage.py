#!/usr/bin/env python3
import itertools
from typing import Dict, Optional, Union

from pyudmf.model.textmap import Textmap, Vertex, Sector, Sidedef, Linedef, Thing


class Visage(object):
    # TODO remove textmap param altogether? or factory method for convertion textmap into dict
    def __init__(self, textmap: Textmap, dct: Optional[Dict] = None):
        if dct is None:
            index_generator = itertools.count(start=0, step=1)
            self._namespace = {'global_index': next(index_generator)}
            self._sectors = {s: {'global_index': next(index_generator)} for s in textmap.sectors}
            self._vertices = {v: {'global_index': next(index_generator)} for v in textmap.vertices}
            self._sidedefs = {sd: {'global_index': next(index_generator)} for sd in textmap.sidedefs}
            self._linedefs = {sd: {'global_index': next(index_generator)} for sd in textmap.linedefs}
            self._things = {v: {'global_index': next(index_generator)} for v in textmap.things}
        else:
            self._vertices = dct['vertices']
            self._sectors = dct['sectors']
            self._sidedefs = dct['sidedefs']
            self._linedefs = dct['linedefs']
            self._things = dct['things']
            self._namespace = dct['namespace']

    def thing_id(self, thing: Thing) -> int:
        global_index = self._things[thing]['global_index']
        global_indices = sorted(s['global_index'] for s in self._things.values())
        return global_indices.index(global_index)

    def vertex_id(self, vertex: Vertex) -> int:
        global_index = self._vertices[vertex]['global_index']
        global_indices = sorted(s['global_index'] for s in self._vertices.values())
        return global_indices.index(global_index)

    def sector_id(self, sector: Sector) -> int:
        global_index = self._sectors[sector]['global_index']
        global_indices = sorted(s['global_index'] for s in self._sectors.values())
        return global_indices.index(global_index)

    def sidedef_id(self, sidedef: Sidedef) -> int:
        global_index = self._sidedefs[sidedef]['global_index']
        global_indices = sorted(s['global_index'] for s in self._sidedefs.values())
        return global_indices.index(global_index)

    def linedef_id(self, linedef: Linedef) -> int:
        global_index = self._linedefs[linedef]['global_index']
        global_indices = sorted(s['global_index'] for s in self._linedefs.values())
        return global_indices.index(global_index)

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
