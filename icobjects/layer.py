import json
import logging
from write.logger import *

class GenericLayer:
    '''Represents any possible layer'''
    log = logging.getLogger()
    def __init__(self, name, num, purpose, points):
        self.name = name
        self.num = num
        self.purpose = purpose
        self.points = points
        log.info("GenericLayer: {} {} {} {}".format(name, num, purpose, points))

    def tell(self):
        print("\t=== Layer Info ===\n\
        Name: {}\n\
        Number: {}\n\
        Purpose: {}\n\
        Points: {}".format(self.name, self.num, self.purpose, self.points))

    def to_json(self):
        return json.dumps(self.__dict__)

class MaskLayer(GenericLayer):
    '''Represents a mask layer'''
    log = logging.getLogger()
    def __init__(self, name, num, purpose, points, stack, multi_pattern, net,\
    dir, volt_hi, volt_lo):
        GenericLayer.__init__(self, name, num, purpose, points)
        self.stack = stack
        self.multi_pattern = multi_pattern
        self.net = net
        self.dir = dir
        self.volt_hi = volt_hi
        self.volt_lo = volt_lo
        log.info("MaskLayer: {} {} {} {} {} {} {} {} {} {}".format(name, num,\
        purpose, points, stack, multi_pattern, net, dir, volt_hi, volt_lo))

    def tell(self):
        GenericLayer.tell(self)
        print("\tStack: {}\n\
        Multi-Patterning Color: {}\n\
        Net Name: {}\n\
        Direction: {}\n\
        High Voltage: {}\n\
        Low Voltage: {}".format(self.stack, self.multi_pattern, self.net,\
        self.dir, self.volt_hi, self.volt_lo)
        )

class CadLayer(GenericLayer):
    '''Represents a CAD layer'''
    log = logging.getLogger()
    def __init__(self, name, num, purpose, points):
        GenericLayer.__init__(self, name, num, purpose, points)
        log.info("CadLayer: {} {} {} {}".format(self.name, self.num,\
        self.purpose, self.points))
    def tell(self):
        GenericLayer.tell(self)
