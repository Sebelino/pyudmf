#!/usr/bin/env python

import pytest

from pyudmf.parser import parse_udmf, TranslationUnit, Assignment, Block
from pyudmf.main import scaled


@pytest.mark.parametrize("textmap, expected", [
    ('', TranslationUnit()),
    ('namespace = "zdoom";', TranslationUnit(Assignment('namespace', 'zdoom'))),
    ('namespace = "zdoom"; thing {}', TranslationUnit(Assignment('namespace', 'zdoom'), Block('thing', []))),
    ('namespace = "zdoom"; thing { x = 7; }', TranslationUnit(Assignment('namespace', 'zdoom'),
                                                              Block('thing', [Assignment('x', 7)]))),
    ('thing { type = 3001; }', TranslationUnit(Block('thing', [Assignment('type', 3001)]))),
    ('thing { angle = 90; }', TranslationUnit(Block('thing', [Assignment('angle', 90)]))),
    ('thing { ambush = true; }', TranslationUnit(Block('thing', [Assignment('ambush', True)]))),
    ('thing { coop = true; }', TranslationUnit(Block('thing', [Assignment('coop', True)]))),
    ('thing { dm = true; }', TranslationUnit(Block('thing', [Assignment('dm', True)]))),
    ('thing { single = true; }', TranslationUnit(Block('thing', [Assignment('single', True)]))),
    ('thing { skill1 = true; }', TranslationUnit(Block('thing', [Assignment('skill1', True)]))),
    ('thing { skill2 = true; }', TranslationUnit(Block('thing', [Assignment('skill2', True)]))),
    ('thing { skill3 = true; }', TranslationUnit(Block('thing', [Assignment('skill3', True)]))),
    ('thing { skill4 = true; }', TranslationUnit(Block('thing', [Assignment('skill4', True)]))),
    ('thing { skill5 = true; }', TranslationUnit(Block('thing', [Assignment('skill5', True)]))),
    ('linedef { v1 = 0; }', TranslationUnit(Block('linedef', [Assignment('v1', 0)]))),
    ('linedef { v2 = 1; }', TranslationUnit(Block('linedef', [Assignment('v2', 1)]))),
    ('linedef { sidefront = 0; }', TranslationUnit(Block('linedef', [Assignment('sidefront', 0)]))),
    ('linedef { sideback = 37; }', TranslationUnit(Block('linedef', [Assignment('sideback', 37)]))),
    ('linedef { blocking = true; }', TranslationUnit(Block('linedef', [Assignment('blocking', True)]))),
    ('linedef { dontpegtop = true; }', TranslationUnit(Block('linedef', [Assignment('dontpegtop', True)]))),
    ('linedef { dontpegbottom = true; }', TranslationUnit(Block('linedef', [Assignment('dontpegbottom', True)]))),
    ('linedef { blocking = true; }', TranslationUnit(Block('linedef', [Assignment('blocking', True)]))),
    ('linedef { blocksound = true; }', TranslationUnit(Block('linedef', [Assignment('blocksound', True)]))),
    ('linedef { twosided = true; }', TranslationUnit(Block('linedef', [Assignment('twosided', True)]))),
    ('linedef { playercross = true; }', TranslationUnit(Block('linedef', [Assignment('playercross', True)]))),
    ('linedef { special = 12; }', TranslationUnit(Block('linedef', [Assignment('special', 12)]))),
    ('linedef { arg0 = 7; }', TranslationUnit(Block('linedef', [Assignment('arg0', 7)]))),
    ('linedef { arg1 = 57; }', TranslationUnit(Block('linedef', [Assignment('arg1', 57)]))),
    ('linedef { arg2 = 50; }', TranslationUnit(Block('linedef', [Assignment('arg2', 50)]))),
    ('linedef { arg3 = 5; }', TranslationUnit(Block('linedef', [Assignment('arg3', 5)]))),
    ('linedef { playeruse = true; }', TranslationUnit(Block('linedef', [Assignment('playeruse', True)]))),
    ('linedef { repeatspecial = true; }', TranslationUnit(Block('linedef', [Assignment('repeatspecial', True)]))),
    ('linedef { monsteruse = true; }', TranslationUnit(Block('linedef', [Assignment('monsteruse', True)]))),
    ('linedef { id = 78; }', TranslationUnit(Block('linedef', [Assignment('id', 78)]))),
    ('sidedef { sector = 2; }', TranslationUnit(Block('sidedef', [Assignment('sector', 2)]))),
    ('sidedef { texturetop = "ab"; }', TranslationUnit(Block('sidedef', [Assignment('texturetop', "ab")]))),
    ('sidedef { texturemiddle = "ab"; }', TranslationUnit(Block('sidedef', [Assignment('texturemiddle', "ab")]))),
    ('sidedef { texturebottom = "ab"; }', TranslationUnit(Block('sidedef', [Assignment('texturebottom', "ab")]))),
    ('sidedef { offsetx = 256; }', TranslationUnit(Block('sidedef', [Assignment('offsetx', 256)]))),
    ('sector { texturefloor = "bc"; }', TranslationUnit(Block('sector', [Assignment('texturefloor', "bc")]))),
    ('sector { textureceiling = "bc"; }', TranslationUnit(Block('sector', [Assignment('textureceiling', "bc")]))),
    ('sector { heightceiling = 128; }', TranslationUnit(Block('sector', [Assignment('heightceiling', 128)]))),
    ('sector { heightfloor = 8; }', TranslationUnit(Block('sector', [Assignment('heightfloor', 8)]))),
    ('sector { lightlevel = 156; }', TranslationUnit(Block('sector', [Assignment('lightlevel', 156)]))),
    ('sector { xscalefloor = 3.0; }', TranslationUnit(Block('sector', [Assignment('xscalefloor', 3.0)]))),
    ('sector { yscalefloor = 3.0; }', TranslationUnit(Block('sector', [Assignment('yscalefloor', 3.0)]))),
    ('sector { xscaleceiling = 3.0; }', TranslationUnit(Block('sector', [Assignment('xscaleceiling', 3.0)]))),
    ('sector { yscaleceiling = 3.0; }', TranslationUnit(Block('sector', [Assignment('yscaleceiling', 3.0)]))),
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
    (Assignment('v1', 7), 'v1 = 7;'),
    (Assignment('x', 77.0), 'x = 77.0;'),
    (Assignment('coop', True), 'coop = true;'),
    (Assignment('coop', False), 'coop = false;'),
    (Assignment('namespace', 'zdoom'), 'namespace = "zdoom";'),
])
def test_str(ast, expected):
    assert str(ast) == expected


@pytest.mark.parametrize("ast, expected", [
    (TranslationUnit(Assignment('namespace', 'zdoom'), Block('thing', [Assignment('x', 7.0), Assignment('y', 8.0)])),
     TranslationUnit(Assignment('namespace', 'zdoom'),
                     Block('thing', [Assignment('x', 3.5), Assignment('y', 4.0)]))),
])
def test_scaled(ast, expected):
    returned = scaled(ast, 0.5)
    assert returned == expected


@pytest.mark.parametrize("textmap, expected", [
    ('v1 = 7;', 'v1 = 7;'),
    ('x = 77.0;', 'x = 77.0;'),
])
def test_bijection(textmap, expected):
    assert str(parse_udmf(textmap)) == expected
