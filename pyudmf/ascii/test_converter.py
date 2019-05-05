#!/usr/bin/env python3

import pytest

from pyudmf.ascii.converter import asciimap2textmap, generate_linedefs
from pyudmf.model.textmap import Textmap, Vertex, Sector, Sidedef, Thing, Linedef


@pytest.fixture()
def sample_asciimap():
    return [
        "...",
        "...",
    ]


@pytest.fixture()
def sample_vertices():
    return [
        [Vertex(0, 0), Vertex(64, 0), Vertex(128, 0), Vertex(192, 0)],
        [Vertex(0, 64), Vertex(64, 64), Vertex(128, 64), Vertex(192, 64)],
        [Vertex(0, 128), Vertex(64, 128), Vertex(128, 128), Vertex(192, 128)],
    ]


@pytest.fixture()
def sample_sectors():
    return [
        Sector(0, 128, "MFLR8_1", "MFLR8_1"),
    ]


@pytest.fixture()
def sample_sidedefs(sample_sectors):
    return [
        Sidedef(sample_sectors[0], "STONE2"),
    ]


@pytest.fixture()
def sample_spanning_textmap():
    vertices = [
        Vertex(0, 0),
        Vertex(0, 128),
        Vertex(192, 128),
        Vertex(192, 0),
    ]
    return Textmap(
        vertices=set(vertices),
    )


@pytest.fixture()
def sample_linedefs(sample_vertices, sample_sidedefs):
    vertices = sample_vertices
    sidedefs = sample_sidedefs
    return [
        Linedef(vertices[0][0], vertices[1][0], sidedefs[0]),
        Linedef(vertices[1][0], vertices[1][1], sidedefs[0]),
        Linedef(vertices[1][1], vertices[0][1], sidedefs[0]),
        Linedef(vertices[0][1], vertices[0][0], sidedefs[0]),

        Linedef(vertices[1][1], vertices[1][2], sidedefs[0]),
        Linedef(vertices[1][2], vertices[0][2], sidedefs[0]),
        Linedef(vertices[0][2], vertices[0][1], sidedefs[0]),

        Linedef(vertices[1][2], vertices[1][3], sidedefs[0]),
        Linedef(vertices[1][3], vertices[0][3], sidedefs[0]),
        Linedef(vertices[0][3], vertices[0][2], sidedefs[0]),

        Linedef(vertices[1][0], vertices[2][0], sidedefs[0]),
        Linedef(vertices[2][0], vertices[2][1], sidedefs[0]),
        Linedef(vertices[2][1], vertices[1][1], sidedefs[0]),

        Linedef(vertices[2][1], vertices[2][2], sidedefs[0]),
        Linedef(vertices[2][2], vertices[1][2], sidedefs[0]),

        Linedef(vertices[2][2], vertices[2][3], sidedefs[0]),
        Linedef(vertices[2][3], vertices[1][3], sidedefs[0]),
    ]


@pytest.fixture()
def sample_textmap(sample_vertices, sample_sectors, sample_sidedefs, sample_linedefs):
    things = (
        Thing(1, 32, 32),
    )
    return Textmap(
        vertices=set(v for row in sample_vertices for v in row),
        sectors=set(sample_sectors),
        sidedefs=set(sample_sidedefs),
        linedefs=set(sample_linedefs),
        things=things,
    )


def test_generate_linedefs(sample_vertices, sample_sidedefs, sample_linedefs):
    vertices = {v for lst in sample_vertices for v in lst}
    linedefs = generate_linedefs(vertices, sample_sidedefs)
    assert len(sample_linedefs) == len(linedefs)
    assert set() == {frozenset([ld.v1, ld.v2]) for ld in sample_linedefs}.difference(
        {frozenset([ld.v1, ld.v2]) for ld in linedefs})
    assert set() == {frozenset([ld.v1, ld.v2]) for ld in linedefs}.difference(
        {frozenset([ld.v1, ld.v2]) for ld in sample_linedefs})
    assert {frozenset([ld.v1, ld.v2]) for ld in sample_linedefs} == {frozenset([ld.v1, ld.v2]) for ld in linedefs}
    assert {(ld.v1, ld.v2) for ld in sample_linedefs} == {(ld.v1, ld.v2) for ld in linedefs}
    assert set(sample_linedefs) == linedefs


def test_converter(sample_asciimap, sample_textmap):
    returned = asciimap2textmap(sample_asciimap)

    assert sample_textmap.vertices == returned.vertices
    assert sample_textmap.sectors == returned.sectors
    assert sample_textmap.sidedefs == returned.sidedefs
    assert sample_textmap.linedefs == returned.linedefs
    assert sample_textmap.things == returned.things
    assert sample_textmap == returned
