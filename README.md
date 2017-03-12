# svg-pad-shrink
Script to shrink pads on an svg for solder paste stencils. This will find all rectangular paths and shrink them by N mils.

## usage
usage: `svg_pad_shrink.py [-h] infile mil_to_shrink outfile`

This will shrink all svg pads by N mils

positional arguments:
-  `infile`         input filename
-  `mil_to_shrink`  N mils to shrink pads by
-  `outfile`        output filename
