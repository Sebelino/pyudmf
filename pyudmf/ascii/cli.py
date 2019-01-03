#!/usr/bin/env python3

import argparse

from pyudmf.ascii.converter import asciimap2textmap
from pyudmf.model.factory import textmap2ast

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert an ASCII map to a UDMF formatted TEXTMAP lump.")
    parser.add_argument('infile', help="Path to the ASCII map file.")

    args = parser.parse_args()

    with open(args.infile, 'r') as f:
        asciimap = f.readlines()

    textmap = asciimap2textmap(asciimap)
    tu = textmap2ast(textmap)

    print(tu)
