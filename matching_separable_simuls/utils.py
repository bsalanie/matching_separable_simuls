# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_utils.ipynb.

# %% auto 0
__all__ = ['get_root_dir', 'nprepeat_col', 'nprepeat_row', 'legendre_polynomials', 'quantile_transform']

# %% ../nbs/02_utils.ipynb 3
import sys
import numpy as np
from pathlib import Path

from fastcore.test import test_close, test_eq

# %% ../nbs/02_utils.ipynb 4
def get_root_dir(
                    # no argument
    ) -> Path:      # the package directory
    """ returns the package directory """
    root_dir = Path.cwd().parent
#     if platform in ["linux", "linux2"]:        # we are deploying
#         root_dir = Path.cwd().parent
    return root_dir

# %% ../nbs/02_utils.ipynb 5
def nprepeat_col(
    v: np.ndarray,   # a 1-dim array of size `m`
    n: int           # the number of columns requested
) -> np.ndarray:     # a 2-dim array of shape `(m, n)`
    """ create a matrix with `n` columns equal to the vector`v` """
    return np.repeat(v[:, np.newaxis], n, axis=1)


def nprepeat_row(
    v: np.ndarray,   # a 1-dim array of size `n`
    m: int           # the number of rows requested
) -> np.ndarray:     # a 2-dim array of shape `(m, n)`
    """ create a matrix with `m` rows equal to `v` """
    return np.repeat(v[np.newaxis, :], m, axis=0)



# %% ../nbs/02_utils.ipynb 6
def legendre_polynomials(
    x: np.ndarray,      # points where the polynomials are to be evaluated
    max_deg: int,       # maximum degree
    a: float = -1.0,    # start of interval, classically -1
    b: float = 1.0,      # end of interval, classically 1
    no_constant: bool = False       # if True, delete the constant polynomial
    ) -> np.ndarray:    # returns an array of (max_deg+1) arrays of the shape of x
    """ evaluates the Legendre polynomials over x in the interval [a, b] """
    if a > np.min(x):
        sys.exit(f"legendre_polynomials: points below start of interval")
    if b <  np.max(x):
        sys.exit(f"legendre_polynomials: points above end of interval")
    p =np.zeros((x.size, max_deg + 1))
    p0 = np.ones_like(x)
    x_transf = 2.0*(x-a)/(b-a)-1.0
    p1 = x_transf
    p[:, 0] = np.ones_like(x)
    p[:, 1] = x_transf
    for deg in range(2, max_deg+1):
        p2 = (2*deg-1)*(p[:, deg-1]*x_transf)-(deg-1)*p[:, deg-2]
        p[:, deg] = p2/deg
    polys_p = p[:, 1:] if no_constant else p
    return polys_p

# %% ../nbs/02_utils.ipynb 8
def quantile_transform(
    v: np.ndarray        # a vector of counts
    ) -> np.ndarray:     # the corresponding quantiles
    """ transform a vector of counts into the corresponding quantiles """
    n = v.size
    q = np.zeros(n)
    for i in range(n):
        q[i] = np.sum(v <= v[i])/(n+1)
    return q
        

