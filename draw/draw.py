import cv2
import numpy as np
# maybe better to not use matplotlib
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from PIL import Image, ImageDraw

class PlotCell:
    """docstring for PlotCell."""

    def __init__(self, cell):
        self.cell = cell

    def is_valid_cell(self):
        return type(self.cell).__name__ == 'Cell'

    def plot(self):
        clrs = {0: 'y', 1 : 'r', 2 : 'g', 3 : 'b'}
        # fig = plt.figure()
        fix, ax = plt.subplots()
        if self.is_valid_cell():
            # Get bbox and translate to origin
            rects = []
            bbox = self.cell.bbox
            new_bbox = list(((bbox[0][0] - bbox[0][0], bbox[0][1] - bbox[0][1]), (bbox[1][0] - bbox[0][0], bbox[1][1] - bbox[0][1])))
            # create grid based on bbox max/min in appropriate steps
            for obj in self.cell.objects:
                rect = Rectangle(obj.points[0], self.get_width(obj.points), self.get_height(obj.points), alpha=0.4, color=clrs[obj.num])
                rect.set_label(obj.name)
                rects.append(rect)
                # plotting stuff...
            # do stuff...
            collection = PatchCollection(rects, match_original = True)
            ax.add_collection(collection)
            ax.legend(loc='lower center', handles = rects)
            # plt.plot(rects)
            plt.show()
        else:
            print("Invalid Cell")

    def get_width(self, pts):
        x2 = pts[1][0]
        x1 = pts[0][0]
        width = abs(x2 - x1)
        return width

    def get_height(self, pts):
        y2 = pts[2][1]
        y1 = pts[0][1]
        height = abs(y2 - y1)
        return height

if __name__ == '__main__':
    import argparse as ap
    import sys
    sys.path.insert(1, '/Users/rafinazamodeen/Development/ic_layout/auto-polygon-pusher')
    from icobjects.device import *

    parser = ap.ArgumentParser(description='Create a layout of a Spice device')
    parser.add_argument('spice', help='spice device definition')
    parser.add_argument('device_file', help='device definition file')
    parser.add_argument('rule_file', help='rule file')
    args = parser.parse_args()

    c = FormedDevice(args.spice, args.device_file, args.rule_file).create_device()
    PlotCell(c).plot()
