#!/usr/bin/env python3

import pytest

from pyudmf.model.textmap import Textmap, Vertex, Thing
from pyudmf.ops.scaler import scaled


@pytest.mark.parametrize("textmap, expected", [
    (Textmap(), Textmap()),
    (Textmap(vertices={Vertex(10.0, 16.0)}), Textmap(vertices={Vertex(5.0, 8.0)})),
    (Textmap(things=[Thing(1, 20.0, 7.0)]), Textmap(things=[Thing(1, 10.0, 3.5)])),
])
def test_scaled(textmap, expected):
    returned = scaled(textmap, 0.5)
    assert returned == expected
