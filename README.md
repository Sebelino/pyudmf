pyudmf
======
Command-line tool for resizing a Doom map formatted with the Universal Doom Map Format (UDMF).

# Usage
```bash
$ python pyudmf.py -h
usage: pyudmf.py [-h] infile scalingfactor

Scale an UDMF formatted Doom map.

positional arguments:
  infile         Path to the TEXTMAP lump file.
  scalingfactor  Scaling factor. E.g. if the factor is 0.5, the map will
                 shrink to 25 % of its original area.

optional arguments:
  -h, --help     show this help message and exit
```
