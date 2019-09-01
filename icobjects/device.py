import logging
import numpy as np
import yaml
from write.logger import *
from icobjects.instance import *
from icobjects.layer import *
from skimage.transform import AffineTransform

# A generic device should only be given device definitions and a SPICE file (or word)
class GenericDevice:
    """docstring for GenericDevice.
    Takes the info from Spice Netlist and creates the basis for forming a device based on rule and device definition files."""
    # Basically, we want to accept a parsed spice netlist line
    log = logging.getLogger()
    metric_prefixes = {'m':1e-3, 'u':1e-6, 'n':1e-9, 'p':1e-12}

    def __init__(self, spice_dev, device_file, device_perm = 'r', unit_length = 'u', name = None, rotation = 0):
        self.spice_dev = spice_dev
        self.device_file = device_file
        self.device_perm = device_perm
        self.unit_length = unit_length
        self.name = name if name != None else self.get_device_params()['name']
        self.rotation = rotation
        log.info("GenericDevice parameters:\n \
        \tSpice Device: {}\n \
        \tDevice File: {}, with permission: {}\n \
        \tUnit Length: {}\n \
        \tName: {}\n \
        \tRotation: {}".format(spice_dev, device_file, device_perm, unit_length, name, rotation))

    def get_device_params(self):
        device_params = None
        spice_def = self.spice_dev.split()
        if spice_def[0][0] == 'M':
            device_params = {'device' : spice_def[0][0],\
            'name' : spice_def[0],\
            # Keep order of nets and volt the same as parts in device_defs file
            'nets' : [spice_def[2], spice_def[1], spice_def[3], spice_def[4]],\
            # NOTE: volt is hard-coded for now, probably should be part of spice or another file
            'volt' : [(0, 0.96), (0, 0.96), (0, 0.96), (0, 0.96)],\
            'type' : spice_def[5],\
            'length' : float(spice_def[6].split('=')[1][0:-1]) * self.metric_prefixes[spice_def[6].split('=')[1][-1]] / self.metric_prefixes[self.unit_length],\
            'width' : float(spice_def[7].split('=')[1][0:-1]) * self.metric_prefixes[spice_def[7].split('=')[1][-1]] / self.metric_prefixes[self.unit_length]}
        log.info(f"{str(device_params)}")
        return device_params

    def get_device_defs(self, layer_key = 'all_layers'):
        device = self.get_device_params()['device']
        type = self.get_device_params()['type']
        device_defs = None
        try:
            with open(self.device_file, self.device_perm) as df:
                df_yml = yaml.safe_load(df)
            device_defs = df_yml[device][type]
            all_layers = df_yml[layer_key]
        except FileNotFoundError:
            print("File: {}, cannot be found.".format(self.device_file))
            log.error("File: {}, cannot be found.".format(self.device_file))
        return (device_defs, all_layers)

class FormedDevice(GenericDevice):
    '''docstring for FormedDevice.'''
    log = logging.getLogger()
    def __init__(self, spice_dev, device_file, rule_file, device_perm = 'r', rule_perm = 'r', origin = (0, 0), unit_length = 'u', name = None, rotation = 0):
        GenericDevice.__init__(self, spice_dev, device_file, device_perm, unit_length, name, rotation)
        self.rule_file = rule_file
        self.rule_perm = rule_perm
        self.origin = origin
        log.info(f"Rule File: {rule_file}, Permissions: {rule_perm}, Origin: {origin}")

    def get_design_rules(self):
        design_rules = None
        try:
            with open(self.rule_file, self.rule_perm) as rf:
                design_rules = yaml.safe_load(rf)
                log.info(f"Rule file: {self.rule_file}, successfully loaded.")
        except FileNotFoundError:
            print("File: {}, cannot be found.".format(self.rule_file))
            log.error("File: {}, cannot be found.".format(self.rule_file))
        return design_rules

    # *** Create parts of device ***
    # Get parts from device_defs
    # start with gate for mosfet
    def create_device(self):
        dev_parts = None
        dev_parts = self.create_parts()
        bbox = self.get_bbox(layers_list = dev_parts)
        dev = Cell(self.name, dev_parts, self.origin, self.rotation, bbox, './')
        return dev

    def create_parts(self):
        """Create the parts of a device by cross referencing the blue print with the design rules"""
        # Go through all the parts of the blueprint and find their corresponding values
        # in the design_rules file. Construct a stretch matrix from this value. First, check for
        # 'int' in the [1] element of part - there is no reference for this in the design_rules file.
        # This value must be handled separately.
        formed_layers = []
        (device_defs, layers) = GenericDevice.get_device_defs(self)
        device_params = GenericDevice.get_device_params(self)
        design_rules = self.get_design_rules()
        parts = list(device_defs['parts'].keys())
        init_dims = list((self.origin, (self.origin[0] + device_params['length'], self.origin[1]), (self.origin[0] + device_params['length'], self.origin[1] + device_params['width']), (self.origin[0], self.origin[1]+device_params['width'])))
        for net_info, part in enumerate(parts):
            for operation in list(device_defs['parts'][part].keys()):
                # # NOTE: for mosfet, first intersect creates 3 layers
                instructions = device_defs['parts'][part][operation]
                if operation == 'intersect':
                    formed_layers += self.create_intersecting_layers(layers, instructions, init_dims, design_rules, device_params, net_info)
                elif operation == 'extend':
                    #  We need to create a translation matrix for the extensions and create points
                    # instructions = device_defs['parts'][part][operation]
                    formed_layers += self.create_extending_layers(layers, instructions, design_rules, device_params, formed_layers, net_info)
        return formed_layers

    def get_bbox(self, layers_list = None, points_list = None):
        all_points = []
        gety = lambda coord : coord[1]
        if points_list:
            all_points = points_list
        else:
            for layer in layers_list:
                all_points += layer.points
        maxx = sorted(all_points)[-1][0]
        maxy = sorted(all_points, key = gety)[-1][1]
        minx = sorted(all_points, reverse = True)[-1][0]
        miny = sorted(all_points, reverse = True, key = gety)[-1][1]
        bbox = [(minx, miny), (maxx, maxy)]
        return bbox

    def apply_transform(self, direction, ref_layer, ext_layer, layers):
        # In general, the design rules for creating a transformation matrix will be read as:
        # self.design_rules['layer'][first_layer_name][transform_type][second_layer_name][transform_direction]
        # i.e. self.design_rules['layer']['PO drawing']['extend']['OD drawing']['north']
        # PO extension on OD in north direction
        # print(f"D0: {description[0]}, D1: {description[1]}, D2: {description[2]}, D3: {description[3]}\n")
        # First look at the translate in positive or negative y direction
        north = direction['north']
        east = direction['east']
        south = direction['south']
        west = direction['west']

        # NOTE: AffineTransform is only 2D and can only accept (X, Y), hence p_*[:2]
        t_ne = AffineTransform(translation = (east, north))
        t_nw = AffineTransform(translation = (west, north))
        t_se = AffineTransform(translation = (east, south))
        t_sw = AffineTransform(translation = (west, south))

        # We need a function that can pick out all the points of a given layer, then pass those points
        # to get_bbox
        bbox_ref = self.get_bbox(points_list = self.get_layer_points(ref_layer, layers))
        bbox_ext = self.get_bbox(points_list = self.get_layer_points(ext_layer, layers))
        p_ne = (bbox_ref[1][0], bbox_ext[1][1])
        p_nw = (bbox_ref[0][0], bbox_ext[1][1])
        p_se = (bbox_ref[1][0], bbox_ext[0][1])
        p_sw = (bbox_ref[0][0], bbox_ext[0][1])
        t_pts = (t_sw(p_sw), t_se(p_se), t_ne(p_ne), t_nw(p_nw))
        t_pts = list(tuple(p.tolist()[0]) for p in t_pts)
        return t_pts

    def get_layer_points(self, layer_name, layers):
        layer_pts_list = []
        layer_pts_dict = {}
        layer_pts_list = list((' '.join([o.name.split()[0], o.purpose]), o.points) for o in layers)
        for key, value in layer_pts_list:
            if layer_pts_dict.get(key) is None:
                layer_pts_dict.update([(key, value)])
            elif value not in layer_pts_dict[key]:
                layer_pts_dict[key] = layer_pts_dict[key] + value
        return layer_pts_dict[layer_name]

    def create_intersecting_layers(self, layers, instructions, points, rules, params, net_index):
        mask_layers = []
        for instruction in instructions:
            mask_layers.append(MaskLayer(layers[instruction], rules['layer'][layers[instruction]]['number'],\
                layers[instruction].split()[-1], points, layers[instruction].split()[0], rules['layer'][layers[instruction]]['mp'],\
                params['nets'][net_index], rules['layer'][layers[instruction]]['direction'], params['volt'][net_index][1],\
                params['volt'][net_index][0]))
        return mask_layers

    def create_extending_layers(self, req_layers, instructions, rules, params, layers, net_index):
        mask_layers_ext = []
        for instruction in instructions:
            extend_layer = req_layers[int(instruction.split()[0])]
            direction = instruction.split()[1]
            ref_layer = req_layers[int(instruction.split()[2])]
            points = self.apply_transform(rules['layer'][extend_layer]['extend'][ref_layer], ref_layer, extend_layer, layers)
            mask_layers_ext.append(MaskLayer(extend_layer, rules['layer'][extend_layer]['number'],\
                extend_layer.split()[-1], points, extend_layer.split()[0], rules['layer'][extend_layer]['mp'],\
                params['nets'][net_index], rules['layer'][extend_layer]['direction'], params['volt'][net_index][1],\
                params['volt'][net_index][0]))
        return mask_layers_ext

if __name__ == "__main__":
    import argparse as ap

    parser = ap.ArgumentParser(description='Create a layout of a Spice device')
    parser.add_argument('spice', help='spice device definition')
    parser.add_argument('device_file', help='device definition file')
    parser.add_argument('rule_file', help='rule file')
    args = parser.parse_args()
    c = FormedDevice(args.spice, args.device_file, args.rule_file).create_device()
