#!/usr/bin/env python

import pytest

from .udmfscale import parse_udmf, TranslationUnit, Assignment, Block, scaled


@pytest.mark.parametrize("textmap, expected", [
    ('', TranslationUnit()),
    ('namespace = "zdoom";', TranslationUnit(Assignment('namespace', 'zdoom'))),
    ('namespace = "zdoom"; thing {}', TranslationUnit(Assignment('namespace', 'zdoom'), Block('thing', []))),
    ('namespace = "zdoom"; thing { x = 7; }', TranslationUnit(Assignment('namespace', 'zdoom'),
                                                              Block('thing', [Assignment('x', 7)]))),
    ("""
thing
{
x = 608.000;
y = 256.000;
angle = 90;
ambush = true;
}
    """,
     TranslationUnit(
         Block("thing", [
             Assignment('x', 608.000),
             Assignment('y', 256.000),
             Assignment('angle', 90),
             Assignment('ambush', True),
         ])
     )),
    ("""
sidedef
{
sector = 7;
}

sector
{
texturefloor = "FLOOR6_2";
textureceiling = "CEIL3_5";
heightceiling = 128;
lightlevel = 156;
}
    """,
     TranslationUnit(
         Block("sidedef", [
             Assignment("sector", 7),
         ]),
         Block("sector", [
             Assignment("texturefloor", "FLOOR6_2"),
             Assignment("textureceiling", "CEIL3_5"),
             Assignment("heightceiling", 128),
             Assignment("lightlevel", 156),
         ])
     )),
])
def test_parse_udmf(textmap, expected):
    returned = parse_udmf(textmap)
    assert returned == expected


@pytest.mark.parametrize("ast, expected", [
    (Assignment('x', 7), 'x = 7;'),
    (Assignment('coop', True), 'coop = true;'),
    (Assignment('coop', False), 'coop = false;'),
    (Assignment('namespace', 'zdoom'), 'namespace = "zdoom";'),
])
def test_str(ast, expected):
    assert str(ast) == expected


@pytest.mark.parametrize("ast, expected", [
    (TranslationUnit(Assignment('namespace', 'zdoom'), Block('thing', [Assignment('x', 7), Assignment('y', 8)])),
     TranslationUnit(Assignment('namespace', 'zdoom'),
                     Block('thing', [Assignment('x', 3.5), Assignment('y', 4)]))),
])
def test_scaled(ast, expected):
    returned = scaled(ast, 0.5)
    assert returned == expected
