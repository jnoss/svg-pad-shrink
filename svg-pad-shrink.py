#!/usr/bin/env python

from lxml import etree
import re
import argparse

class SVG_Pad_Shrink:
    MIL_TO_PT = 0.01388729089

    def __init__(self, infile, outfile, shrink_mil):
        self.infile = infile
        self.outfile = outfile
        self.shrink_mil = int(shrink_mil)

    def import_svg(self):
        with open(self.infile, 'r') as infile:
            self.tree = etree.parse( infile )
        infile.close()

    def start_from_string(self, string):
        start_re = 'm ([0-9\.]*,[0-9\.]*) .*'
        start = re.sub(start_re,'\\1',string)
        start_arr = start.split(',')
        return (float(start_arr[0]), float(start_arr[1]))

    def points_from_string(self, string):
        points_re = 'm [0-9\.]*,[0-9\.]* ([\-0-9\.]*,[\-0-9\.]*) ([\-0-9\.]*,[\-0-9\.]*) ([\-0-9\.]*,[\-0-9\.]*) z.*'
        points = re.sub(points_re,'\\1 \\2 \\3',string)
        points_arr = points.split(' ')
        point_coord_ret = []
        for point in points_arr:
            point_coord_arr = point.split(',')
            point_coord_ret.append((float(point_coord_arr[0]), float(point_coord_arr[1])))
        return(point_coord_ret)

    def check_four_points(self, string):
        points_re = 'm [0-9\.]*,[0-9\.]* ([\-0-9\.]*,[\-0-9\.]*) ([\-0-9\.]*,[\-0-9\.]*) ([\-0-9\.]*,[\-0-9\.]*) z.*'
        if re.match(points_re,string):
            return True
        return False

    def new_start(self, start):
        shrinkage = self.shrink_mil * self.MIL_TO_PT
        # FIXME svg coords y opposite inkscape
        shrink_tuple = (shrinkage, -shrinkage)
        # FIXME this always goes +x +y should check that matches the path orientation
        return tuple(map(sum,zip(start, shrink_tuple)))

    def new_points(self, points):
        shrinkage = self.shrink_mil * self.MIL_TO_PT
        point_coord_ret = []
        for point in points:
            if point[0] > 0:
                # FIXME handle for non horizontal
                point_coord_ret.append((point[0]-2*shrinkage,0))
            if point[0] < 0:
                point_coord_ret.append((point[0]+2*shrinkage,0))
            if point[1] > 0:
                # FIXME handle for non horizontal
                point_coord_ret.append((0,point[1]-2*shrinkage))
            if point[1] < 0:
                point_coord_ret.append((0,point[1]+2*shrinkage))
        return point_coord_ret

    def write_string(self, start, points):
        string = "m {startx},{starty} {point1x},{point1y} {point2x},{point2y} {point3x},{point3y} z m 0,0"
        return string.format(startx=start[0],
                             starty=start[1],
                             point1x=points[0][0],
                             point1y=points[0][1],
                             point2x=points[1][0],
                             point2y=points[1][1],
                             point3x=points[2][0],
                             point3y=points[2][1],
                            )

    def shrink_path(self, pathstring):
        shrunken_path=self.write_string(self.new_start(self.start_from_string(pathstring)),
                 self.new_points(self.points_from_string(pathstring)))
        return shrunken_path


    def difference(self, tuple):
        return tuple[1] - tuple[0]

    def start_diff(self, old_start, new_start):
        return(tuple(map(self.difference,zip(old_start, new_start))))

    def points_diff(self, old_points, new_points):
        point_diff_ret = []
        for old_point, new_point in zip(old_points, new_points):
            point_diff_ret.append(tuple(map(self.difference,zip(old_point, new_point))))
        return point_diff_ret

    def shrink_all(self):
        for path in self.tree.findall('{http://www.w3.org/2000/svg}path'):
            pathstring = path.get('d')
            if self.check_four_points(pathstring):
                shrunken_path = self.shrink_path(pathstring)
                path.set('d', shrunken_path)

    def write_out(self):
        f = open(self.outfile, 'w')
        f.write(etree.tostring(self.tree).decode('unicode_escape'))
        f.close()

    def shrink_wrapper(self):
        self.import_svg()
        self.shrink_all()
        self.write_out()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="shrink svg pads by N mils")
    parser.add_argument('infile', help='input filename')
    parser.add_argument('mil_to_shrink', help='N mils to shrink pads by')
    parser.add_argument('outfile', help='output filename')

    args = parser.parse_args()

    svg_pad_shrink = SVG_Pad_Shrink(infile=args.infile, outfile=args.outfile, shrink_mil=args.mil_to_shrink)
    svg_pad_shrink.shrink_wrapper()

    print("done, %s written" % args.outfile)
