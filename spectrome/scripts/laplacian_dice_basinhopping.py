"""
Use the basinhopping algorithm to find best alpha, speed, and frequency
that produces the best DICE scores for a given canonical network
"""

# number stuff imports
import h5py
import numpy as np
import pandas as pd
from scipy.optimize import basinhopping
from sklearn.linear_model import LinearRegression

import sys
import os

# spectrome imports
from spectrome.brain import Brain
from spectrome.utils import functions, path
from spectrome.forward import eigenmode, get_complex_laplacian

# hcp template connectome directory
hcp_dir = "../data"

HCP_brain = Brain.Brain()
HCP_brain.add_connectome(hcp_dir)
HCP_brain.reorder_connectome(HCP_brain.connectome, HCP_brain.distance_matrix)
HCP_brain.bi_symmetric_c()
HCP_brain.reduce_extreme_dir()

# Load Pablo's Yeo 2017 canonical network maps
com_dk = np.load(
    "../data/com_dk.npy",
    allow_pickle = True
).item()
DK_df_normalized = pd.read_csv(
    "../data/DK_dictionary_normalized.csv"
).set_index("Unnamed: 0")

# binarize:
ub, lb = 1, 0 #define binary boundaries

DKfc_binarized = pd.DataFrame(
    [], index=DK_df_normalized.index, columns=DK_df_normalized.columns
)
for name in DK_df_normalized.index:
    u = np.mean(np.nan_to_num(DK_df_normalized.loc[name].values))
    s = np.std(np.nan_to_num(DK_df_normalized.loc[name].values))
    threshold = u - s * 0.1
    DKfc_binarized.loc[name] = np.where(
        DK_df_normalized.loc[name].values > threshold, ub, lb
    )

def laplacian_dice(x, Brain, FC_networks, network_name):
    # Define frequency of interest
    w = 2 * np.pi * x[0]
    
    # Laplacian, Brain already prep-ed with connectomes outside of function:
    Brain.add_laplacian_eigenmodes(w=w, alpha = x[1], speed = x[2], num_ev = 86)
    # Dice:
    Brain.binary_eigenmodes = np.where(Brain.norm_eigenmodes > 0.6, 1, 0)
    hcp_dice = eigenmode.get_dice_df(Brain.binary_eigenmodes, FC_networks)
    # Compute mean Dice for chosen network:
    ntw_dice = np.round(hcp_dice[network_name].values.astype(np.double),3)
    min_dice = np.min(ntw_dice)
    return min_dice

class BH_bounds(object):
    def __init__(self, xmax = [45, 5, 30], xmin = [1, 0, 0]):
        self.xmax = np.array(xmax)
        self.xmin = np.array(xmin)
    
    def __call__(self, **kwargs):
        x = kwargs["x_new"]
        tmax = bool(np.all(x <= self.xmax))
        tmin = bool(np.all(x >= self.xmin))
        return tmax and tmin


bnds = BH_bounds()
opt_res = basinhopping(
    laplacian_dice, x0 = (2,0.5,10),
    minimizer_kwargs = {"args":(HCP_brain, DKfc_binarized, str(sys.argv[1]))},
    niter=500,
    T = 0.01,
    stepsize = 1.2,
    accept_test = bnds,
    disp=False)

opt_freq = opt_res['x'][0]
opt_alpha = opt_res['x'][1]
opt_speed = opt_res['x'][2]

print('optimized parameters: {}'.format(opt_res['x']))
# Recreate the forward solution:
w_opt = 2*np.pi*opt_freq
HCP_brain.add_laplacian_eigenmodes(w=w_opt, alpha = opt_alpha, speed = opt_speed)
HCP_brain.binary_eigenmodes = np.where(HCP_brain.binary_eigenmodes > 0.6, 1, 0)
opt_dice = eigenmode.get_dice_df(HCP_brain.binary_eigenmodes, DKfc_binarized)
ntw_opt_dice = np.round(opt_dice[str(sys.argv[1])].values.astype(np.double),3)
print('all dice scores: {}'.format(ntw_opt_dice_dice))
min_opt_dice = np.min(ntw_opt_dice)

print('Basin hopping final dice: {}'.format(opt_res['fun']))
print('Forward calculated dice : {}'.format(min_opt_dice))
assert min_opt_dice == np.round(opt_res['fun'],3)

# Linear Regression for 10 K's and save in a dictionary:
K = 11
ordered_dice = np.argsort(ntw_opt_dice)
assert ntw_opt_dice[ordered_dice[1]] > ntw_opt_dice[ordered_dice[0]]

# create empty list of dicts:
LinReg = []
keys = ['num','coef','r2score','ordereigs']
for k in np.arange(1,K):
    selected_eigs = HCP_brain.norm_eigenmodes[:,ordered_dice[0:k]]
    canon_network = np.nan_to_num(DK_df_normalized.loc[str(sys.argv[1])].values).reshape(-1,1)
    regr = LinearRegression()
    regr.fit(canon_network, selected_eigs)
    c = regr.coef_
    r2 = regr.score(canon_network, selected_eigs)
    reg_results = {keys[0]:k, keys[1]:c, keys[2]:r2, keys[3]:ordered_dice[0:k]}
    LinReg.append(reg_results)
    print('For K = {}, chosen eigs: {}, coefficients: {} , residual error: {}'.format(k, ordered_dice[0:k], c, r2))

opt_res['LinRegResults'] = LinReg
file_name = str(sys.argv[1]) + "_BH_dice.h5"
file_path = os.path.join(hcp_dir, file_name)
path.save_hdf5(file_path, opt_res)
print("Optimal result: " , opt_res['x'])