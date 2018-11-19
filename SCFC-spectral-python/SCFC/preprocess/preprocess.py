'''functions to make sure that data is in the right order, or that data is given dictionary
keys labelling the data according to the brain regions'''

import sys, os
sys.path.append("..")
from utils import path as pth
from scipy.io import loadmat
import re
import csv
import numpy as np


def add_key_data(label_filepath, data_filepath):
    """Add dictionary keys (brain regions) to MEG data from raw MAT files
    (note that this currently works for one particularly style of brain region input,
    and will be generalised in future). The ordering used here is the desikan ordering.

    Args:
        label_filepath (type): full path and filename of the file containing the
        correct order for the data being passed.
        data_filepath (type): full path and filename of data MAT file.

    Returns:
        type: a dictionary of the data, keyed by brain region.

    """


    label_file = open(label_filepath, "r")
    lines = label_file.readlines()
    label_file.close()

    #hack for Chang's data -- cleaning up ROIs list format -- can change for other versions
    #of data
    i = 0
    for line in lines:
        index_stop = line.find('.')
        ind_newline = line.find('\n')
        lines[i] = line[index_stop+1:ind_newline].lower()
        i += 1

    #import the data and apply the list members as keys, resave data in better format
    data = loadmat(data_filepath)
    data = data['DK_timecourse']

    data_dict ={}
    for keys, values in zip(lines, data[:,:]):
        data_dict[keys] = values

    return data_dict

def add_key_coords(label_filepath, coordfile):
    """Add dictionary keys (brain regions) to brain region coordinates from raw MAT files
    (note that this currently works for one particularly style of brain region input,
    and will be generalised in future).

    Args:
        label_filepath (type): full path and filename of the file containing the
        correct order for the data being passed.
        coordfile (type): full path and filename of coord MAT file.

    Returns:
        type: dictionary of coordinates, keyed by brain region.

    """
    label_file = open(label_filepath, "r")
    lines = label_file.readlines()
    label_file.close()

    i = 0
    for line in lines:
        index_stop = line.find('.')
        ind_newline = line.find('\n')
        lines[i] = line[index_stop+1:ind_newline].lower()
        i += 1

    coords = loadmat(coordfile)
    coords = coords['DK_coords_meg']

    coord_dict ={}
    for keys, values in zip(lines, coords):
        coord_dict[keys] = values
    return coord_dict

# def label_connectivity():

def get_desikan(filepath):
    """Parse the desikan atlas ordering for the 68 cortical regions from the csv file,
    or indeed any other csv dictionary.

    Args:
        filepath (type): full file path.

    Returns:
        regions: list of region names in order of the desikan atlas.
        coords: the coordinates of the desikan atlas, in the same order.

    """
    with open(filepath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        regions = []
        coords = []
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                regions.append(row[1])
                x = float(row[2])
                y = float(row[3])
                z = float(row[4])
                coords.append([x,y,z])
    return regions, coords

def HCP_get_order(filepath, save=False, fileout = None):
    """Import the HCP connectome, and create a dictionary with the same order so
    that input data can be rearranged to compare. The dictionary keys are standardised to single
    words, lower case only.

    Args:
        filepath (type): Path to HCP connectome file.
        save (type): Save output list to file?
        fileout (type): Location of output list.

    Returns:
        type: List of the brain regions in order, with cortical regions formatted in standard
        lower case, single word with no spaces.

    """

    with open(filepath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        region_order = []
        for row in csv_reader:
            if line_count == 0:
                for cell in row:
                    index = cell.find('ctx')
                    if index != -1:
                        cell = cell[index+7:]
                        region_order.append(cell.lower())
                    else:
                        cell = cell
                        region_order.append(cell)
                line_count += 1
            else:
                break

    if save:
        pth.save_hdf5(fileout, region_order)

    return region_order




if __name__ == "__main__":

    # labelfile = 'desikan_atlas_68.csv'
    # label_path = pth.get_sibling_path('dictionaries')
    # label_filename = os.path.join(label_path, labelfile)
    # regions, coords = get_desikan(label_filename)
    # print(regions)
    # print(coords)

    # labelfile = 'mean80_fibercount.csv'
    # outlist = 'HCP_list.h5'
    # label_path = pth.get_sibling_path('data')
    # label_filename = os.path.join(label_path, labelfile)
    # out_filename = os.path.join(label_path, outlist)
    # regions = HCP_get_order(label_filename, save = True, fileout = out_filename)
    # print(regions)


    # '''example of the use of this -- preprocessed Chang's data accordingly'''
    # datapath = '/Users/Megan/RajLab/MEG-chang'
    # directories = pth.walk_tree(datapath)
    # coord_filename = 'DK_coords_meg.mat'
    # data_filename = 'DK_timecourse_20.mat'
    # out_coords = 'DK_coords_meg.h5'
    # out_data = 'DK_timecourse_20.h5'
    #
    # labelfile = 'OrderingAlphabetical_68ROIs.txt'
    # label_path = pth.get_sibling_path('dictionaries')
    # label_filename = os.path.join(label_path, labelfile)
    #
    # for dir in directories:
    #     abspath = os.path.join(datapath,dir)
    #     coord_path = os.path.join(abspath, coord_filename)
    #     data_path = os.path.join(abspath, data_filename)
    #
    #     data_dict = add_key_data(label_filename, data_path)
    #     pth.save_hdf5(os.path.join(abspath, out_data), data_dict)
    #
    #     coord_dict = add_key_coords(label_filename, coord_path)
    #     pth.save_hdf5(os.path.join(abspath, out_coords), coord_dict)
