"""Module with generic useful functions such as to return main dir path, and
writing hdf5 files."""

import os
import deepdish as dd

def get_file_path(filename):
    """Find filename in the relative directory `../data/` .

    Args:
        filename (str): file we're looking for in the ./data/ directory.

    Returns:
        str: absolute path to file "filename" in ./data/ dir.

    """
    here_dir = os.path.dirname(os.path.realpath('__file__'))
    file_dir = os.path.join(here_dir, '../data', filename)

    return file_dir


def get_data_path():
    """Return absolute path to `/data/`."""
    here_dir = os.path.dirname(os.path.realpath('__file__'))
    data_path = os.path.join(here_dir, '../data/')

    return data_path


def get_absolute_path(relative_path='.'):
    """Return absolute path given `relative_path`.

    Args:
        relative_path (str): path relative to 'here'.

    Returns:
        str: absolute path

    """
    here_dir = os.path.dirname(os.path.realpath('__file__'))
    abs_path = os.path.join(here_dir, relative_path)

    return abs_path

def get_sibling_path(folder):
    '''returns the path of 'folder' on the same level'''
    here_dir    = os.path.dirname(os.path.realpath('__file__'))
    par_dir = os.path.abspath(os.path.join(here_dir, os.pardir))
    sibling_dir = os.path.join(par_dir, folder)
    return sibling_dir

def save_hdf5(path, dict):
    """Save out a dictionary/numpy array to HDF5 format using deepdish package.

    Args:
        path (type): full path including filename of intended output.
        dict (type): dictionary/numpy array to be saved.

    Returns:
        type: Description of returned object.

    """

    dd.io.save(path, dict)

def read_hdf5(path):
    """Read in dictionary/numpy array from HDF5 format using deepdish package.

    Args:
        path (type): full path including filename of input.

    Returns:
        type: dictionary of data.

    """

    dict = dd.io.load(path)
    return dict

def walk_tree(datapath):
    """Return list of directories in the passed folder.

    Args:
        datapath (type): folder of interest.

    Returns:
        type: list of directories in the passed folder.

    """
    directories = []
    for (path, dirs, files) in os.walk(datapath):
        directories.append(dirs)
    return directories[0]