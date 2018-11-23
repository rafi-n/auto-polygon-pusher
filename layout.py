from icobjects.instance import *
from icobjects.layer import *
from write.write_design import *
from write.logger import *
import numpy as np
import cv2
import pickle
import json

start_oic_logger()
# Testing:
# points will be given as a tuple for now. Later to be converted to np array
pts = [(1,1),(2,2)]
origin = [(0.1,0.1),(0.2,0.2)]
m0 = MaskLayer("M0", 0, "drawing", pts, "M0", "ColorA", "VSS", "horizontal", 0.96, 0.0)
text = CadLayer("text", 1, "drawing", pts)
m0.tell()
text.tell()

objects = [m0, text]
xcell = Cell("newCell", objects, origin, "R0", [(0,0),(100,100)], "./")

m1 = MaskLayer("M1", 0, "drawing", pts, "M1", "ColorB", "VDD", "vertical", 0.96, 0.0)
tpo = CadLayer("TPO", 1, "drawing", pts)
objects2 = [m1, tpo, xcell]
ycell = Cell("newCelly", objects2, origin, "R0", [(0,0),(100,100)], "./")

xcell.tell()
xcell.tell_all()

write_design(xcell)

print("*********\n")
print("*********\n")

print("{}".format(xcell.to_dict()))
input("Press ENTER")

print("{}".format(ycell.to_json()))
input("Press ENTER")
del(xcell)

with open("./newCell.oic", 'rb') as xcell:
    stuff = pickle.load(xcell)
    print(stuff)
    print("*********\n")
    stuff.tell_all()

# json.dumps(stuff.__dict__)
