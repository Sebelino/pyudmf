#!/usr/bin/env python
import argparse

from pyudmf.model.factory import ast2textmap, textmap2ast
from pyudmf.ops.scaler import scaled
from pyudmf.parser import parse_udmf


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scale an UDMF formatted Doom map.")
    parser.add_argument('infile', help="Path to the TEXTMAP lump file.")
    parser.add_argument('scalingfactor', type=float, help="Scaling factor. E.g. if the factor is 0.5, the map will"
                                                          " shrink to 25 %% of its original area.")

    args = parser.parse_args()

    with open(args.infile, 'r') as f:
        textmap_string = f.read().strip()
    ast = parse_udmf(textmap_string)
    textmap, visage = ast2textmap(ast)
    scaled_textmap = scaled(textmap, args.scalingfactor)
    scaled_ast = textmap2ast(scaled_textmap)

    print(scaled_ast)
