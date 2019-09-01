import pickle
import logging
from write.logger import *

# Save a cell as a pickled file
def write_design(cell):
    file_ext = '.oic'
    file=''
    log = logging.getLogger()

    # Make sure the supplied cell is an actual cell class
    if type(cell).__name__=='Cell':
        file = cell.path + '/' + cell.name + file_ext
    else:
        print('write_design only accepts objects of Cell class.')
        log.error("Argument to write_design is not of Cell class. Found: {}\
         instead.".format(type(cell).__name__))

    # Write the cell to a pickle file and handle any exceptions
    try:
        with open(file, 'wb') as outfile:
            try:
                pickle.dump(cell, outfile)
                log.info("Cell: {} written to file: {}".format(cell.name, file))
            except PicklingError:
                print("Cell: {} or object(s) within cell:{} cannot be written.".format(cell.name))
                log.error("Cell: {} or object(s) within it are unpicklable!".format(cell.name))
    except FileNotFoundError:
        print("File: {}, cannot be found.".format(file))
        log.error("File: {}, cannot be found.".format(file))
