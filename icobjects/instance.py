import json
import logging
from write.logger import *

# A cell is a collection of objects: layers and other cells
class Cell:
    """Represents a cell (collection of objects)"""
    # Each cell has a bare minimum of the following properties
    def __init__(self, name, objects, origin, orient, bbox, path):
        log = logging.getLogger()
        self.name = name
        self.objects = objects
        self.origin = origin
        self.orient = orient
        self.bbox = bbox
        self.path = path
        log.info("Cell: {} {} {} {} {} {}".format(self.name, self.objects,\
        self.origin, self.orient, self.bbox, self.path))

    # Convert a cell to a Dictionary
    def to_dict(self):
        log = logging.getLogger()
        dict_obj = []
        for obj in self.objects:
            if hasattr(obj, 'to_dict'):
                dict_obj.append(obj.to_dict())
            else:
                dict_obj.append(obj.__dict__)
        log.info("Created Dictionary for Cell: {}".format(self.name))
        return dict(name=self.name, objects=dict_obj, origin=self.origin,\
        orient=self.orient, bbox=self.bbox, path=self.path)

    # Convert a cell to JSON - references to_dict
    def to_json(self):
        log = logging.getLogger()
        log.info("Created JSON for Cell: {}".format(self.name))
        return json.dumps(self.to_dict(), indent=4)

    # Print out cell properties to the user
    def tell(self):
        log = logging.getLogger()
        print("Cell {} Info:\n\
        Objects: {}\n\
        Origin: {}\n\
        Orientation: {}\n\
        Boundary: {}\n\
        Path: {}".format(self.name, self.objects, self.origin, self.orient,\
        self.bbox, self.path))
        log.info("Told to user for Cell: {}".format(self.name))

    # Print out cell properties recursively to the user
    def tell_all(self):
        log = logging.getLogger()
        self.tell()
        for obj in self.objects:
            if hasattr(obj, 'tell_all'):
                obj.tell_all()
            else:
                obj.tell()
        log.info("Told all to user for Cell: {}".format(self.name))

# A parameterized cell (PCell) is a special type of cell...
class PCell(Cell):
    """Represents a parameterized cell"""
    def __init__(self, name, objects, origin, orient, bbox, path):
        log = logging.getLogger()
        Cell.__init__(self, name, objects, origin, orient, bbox, path)
        log.info("Created PCell: {}".format(self.name))
