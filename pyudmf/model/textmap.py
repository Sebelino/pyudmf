#!/usr/bin/env python3


class Vertex(object):
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return "Vertex({}, {})".format(self.x, self.y)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return isinstance(other, Vertex) and self.x == other.x and self.y == other.y


class Sidedef(object):
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


class Linedef(object):
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


class Sector(object):
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


class Thing(object):
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


class Textmap(object):
    """
    The contents of a TEXTMAP lump.
    """

    def __init__(self, namespace="zdoom", vertices=frozenset(), sidedefs=frozenset(), linedefs=frozenset(),
                 sectors=frozenset(), things=frozenset()):
        self.namespace = namespace
        self.vertices = vertices
        self.sidedefs = sidedefs
        self.linedefs = linedefs
        self.sectors = sectors
        self.things = things

    def __eq__(self, other):
        return isinstance(other, Textmap) and self.vertices == other.vertices

    def __repr__(self):
        return "Textmap(vertices={})".format(self.vertices)
