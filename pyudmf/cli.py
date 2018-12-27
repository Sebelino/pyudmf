#!/usr/bin/env python
import argparse

from pyudmf.ops.scaler import scale
from pyudmf.parser import parse_udmf


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scale an UDMF formatted Doom map.")
    parser.add_argument('infile', help="Path to the TEXTMAP lump file.")
    parser.add_argument('scalingfactor', type=float, help="Scaling factor. E.g. if the factor is 0.5, the map will"
                                                          " shrink to 25 %% of its original area.")

    args = parser.parse_args()

    with open(args.infile, 'r') as f:
        textmap_string = f.read().strip()
    textmap = parse_udmf(textmap_string)
    scale(textmap, args.scalingfactor)
    print(textmap)
