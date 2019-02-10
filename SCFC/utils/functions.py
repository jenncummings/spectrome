import numpy as np
import math

def mag2db(y):
    """Convert magnitude response to decibels for a simple array.

    Args:
        y (numpy array): Power spectrum, raw magnitude response.

    Returns:
        dby (numpy array): Power spectrum in dB

    """
    dby = 20*np.log10(y)
    return dby

def mean_patient(data, freq_number):
    """mean patient: for a patient dictionary of brain region MEG data, find the mean over regions.

    Args:
        data (dict): dictionary keyed by region of data.
        freq_number (int): Length of the frequency list.

    Returns:
        array: array of the mean spectrum across all brain regions for the patient.

    """
    regions = len(list(data.keys()))
    FMEGmean = np.empty((1, freq_number))
    dataarray = np.empty((regions, freq_number))
    i = 0
    for region in data.keys():
        dataarray[i,:] = data[region]
        i += 0
    FMEGmean = np.mean(dataarray, axis = 0)
    return FMEGmean

def down_sample_basic(dataarray, n):
    """down_sample. Down-samples any array in the simplest way possible-- by taking a
    limited number of points from the original array.

    Args:
        dataarray (numpy array): an input data array that needs re-sampling.
        n (int): desired number of output points in the data.

    Returns:
        numpy array: down-sampled data array.

    """

    step = math.floor(len(dataarray)/n)
    output = np.empty(n)
    i = 0
    while i < n:
        j = i*step
        output[i] = dataarray[j]
        i += 1
    return output

def to_float(dataarray):
    """to_float. Ensures input array elements are in correct form of float
    to be accepted by scipy.stats.pearsonr (I genuinely don't know exactly
    why it complains).

    Args:
        dataarray (numpy array/list): An input array of what you think are sensible
        floats but cause scipy.stats.pearsonr to complain.

    Returns:
        array: an array of floats in the right form to stop scipy.stats.pearsonr complaining.

    """
    output = [float(x) for x in dataarray]
    return output