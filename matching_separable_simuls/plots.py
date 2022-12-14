# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_plots.ipynb.

# %% auto 0
__all__ = ['plot_simulation_results']

# %% ../nbs/03_plots.ipynb 4
import pickle
import numpy as np
from typing import Tuple
from fastcore.test import test_eq
from math import sqrt

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn

from cupid_matching.matching_utils import Matching, _get_singles
from cupid_matching.model_classes import ChooSiowPrimitives
from cupid_matching.choo_siow import entropy_choo_siow
from cupid_matching.min_distance import estimate_semilinear_mde
from cupid_matching.poisson_glm import choo_siow_poisson_glm

from .read_data import get_root_dir, read_margins, read_marriages, \
    rescale_mus, reshape_varcov, remove_zero_cells
from .estimate import generate_bases

# %% ../nbs/03_plots.ipynb 5
def plot_simulation_results(
    model_name: str,            # the type of model we are estimating
    n_households_sim: float,    # the number of observed households in the simulation
    value_coeff: float,         # the divider of the smallest positive mu
    n_households_cupid_obs: float = None,    # the number of observed households in the Cupid dataset
) -> None:

    data_dir = get_root_dir() / "matching_separable_simuls" / "ChooSiow70nNdata"
    results_file = data_dir / f"{model_name}_{n_households_sim}_{int(value_coeff)}.pkl"
    with open(results_file, "rb") as f:
        results = pickle.load(f)
    true_coeffs = results['True coeffs']
    if model_name == "choo_siow_cupid":
        varcov_coeffs = results['MDE varcov']
        varcov_rescaled = varcov_coeffs*n_households_cupid_obs/n_households_sim
    estim_mde = results['MDE']
    estim_poisson = results['Poisson']
    base_names = results['Base names']
    n_sim, n_bases = estim_mde.shape
    means_mde = np.mean(estim_mde, 0)
    std_mde = np.std(estim_mde, 0)
    means_poisson = np.mean(estim_poisson, 0)
    std_poisson = np.std(estim_poisson, 0)

    # discard outliers
    beta_err_mde = 4.0*std_mde
    outliers_mde = np.any(abs(estim_mde - means_mde) > beta_err_mde, 1)    # True if simulation has an outlier 
    n_outliers_mde = np.sum(outliers_mde)
    print(f"We have a total of {n_outliers_mde} outliers for MDE, " + f" out of {n_sim} simulations.")
    beta_err_poisson = 4.0*std_poisson
    outliers_poisson = np.any(abs(estim_poisson - means_poisson) > beta_err_poisson, 1)
    n_outliers_poisson = sum(outliers_poisson)
    print(f"We have a total of {n_outliers_poisson} outliers for Poisson, " + f" out of {n_sim} simulations.")

    if max(n_outliers_mde, n_outliers_poisson) > 0:
        kept = [True]*n_sim
        n_discards = 0
        for i in range(n_sim):
            if outliers_mde[i] or outliers_poisson[i]:
                kept[i] = False
                n_discards += 1
        print(f"We are discarding {n_discards} outlier samples")
        kept_mde = estim_mde[kept]
        kept_poisson = estim_poisson[kept]
    else:
        print(f"We have found no outlier samples")
        kept_mde = estim_mde
        kept_poisson = estim_poisson
    n_kept, n_bases = kept_mde.shape
    nkb = n_kept*n_bases
    
    rng = np.random.default_rng(67569)
    
    if model_name == 'choo_siow_cupid':     # we have an 'Expected' curve in the plot
        simulation = np.zeros(3*nkb)
        i = 0
        for i_sim in range(n_kept):
            i_sim_vec = np.full(n_bases, i_sim)
            simulation[i:(i+n_bases)] = i_sim_vec
            simulation[(nkb+i):(nkb+i+n_bases)] = i_sim_vec
            simulation[(2*nkb+i):(2*nkb+i+n_bases)] = i_sim_vec
            i += n_bases
        expected = np.zeros(nkb)
        i = 0
        for i_sim in range(n_kept):
            expected[i:(i+n_bases)] = rng.multivariate_normal(mean=true_coeffs, cov=varcov_rescaled)
            i += n_bases
        estimator = np.array(["MDE"]*nkb + ["Poisson"]*nkb + ["Expected"]*nkb)
        coefficient = base_names*(3*n_kept)
        estimate = np.concatenate((kept_mde.reshape(nkb), 
                               kept_poisson.reshape(nkb),
                              expected.reshape(nkb)))
    else:
        simulation = np.zeros(2*nkb)
        i = 0
        for i_sim in range(n_kept):
            i_sim_vec = np.full(n_bases, i_sim)
            simulation[i:(i+n_bases)] = i_sim_vec
            simulation[(nkb+i):(nkb+i+n_bases)] = i_sim_vec
            i += n_bases
        estimator = np.array(["MDE"]*nkb + ["Poisson"]*nkb)
        coefficient = base_names*(2*n_kept)
        estimate = np.concatenate((kept_mde.reshape(nkb), 
                               kept_poisson.reshape(nkb)))

    df_simul_results = pd.DataFrame(
        {
            "Simulation": simulation,
            "Estimator": estimator,
            "Parameter": coefficient,
            "Estimate": estimate,
        }
    )

    g = sns.FacetGrid(
        data=df_simul_results,
        sharex=False,
        sharey=False,
        hue="Estimator",
        col="Parameter",
        col_wrap=2,
    )
    g.map(sns.kdeplot, "Estimate")
    g.set_titles("{col_name}")
    for true_val, ax in zip(true_coeffs, g.axes.ravel()):
        ax.vlines(true_val, *ax.get_ylim(), color="k", linestyles="dashed")
    g.add_legend()

    plt.savefig(f"{model_name}_simul_results" + f"_{n_households_sim}_{int(value_coeff)}" + ".png")


