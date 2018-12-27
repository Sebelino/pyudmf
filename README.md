pyudmf
======
Command-line tool for resizing a Doom map formatted with the Universal Doom Map Format (UDMF).

# Usage
```bash
$ cd pyudmf
$ python -m pyudmf.main -h
usage: pyudmf.py [-h] infile scalingfactor

Scale an UDMF formatted Doom map.

positional arguments:
  infile         Path to the TEXTMAP lump file.
  scalingfactor  Scaling factor. E.g. if the factor is 0.5, the map will
                 shrink to 25 % of its original area.

optional arguments:
  -h, --help     show this help message and exit
```

## Example
```bash
$ cat TEXTMAP.lmp
namespace = "zdoom";
thing { x = 608.000; y = 256.000; }
vertex { x = 256.000; y = 192.000; }

$ python -m pyudmf.main TEXTMAP.lmp 0.5
namespace = "zdoom";

thing
{
x = 304.000;
y = 128.000;
}

vertex
{
x = 128.000;
y = 96.000;
}
```
