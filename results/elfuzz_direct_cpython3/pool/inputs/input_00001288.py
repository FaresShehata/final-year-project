"""A collection of useful functions about Python."""
from __future__ import division
import numpy as np

def mean_square_error(y, t):
    """Return the mean square error between y and t."""
    return (y - t)**2 / len(t)

def mean_abs_error(y, t):
    """Return the mean absolute error between y and t."""
    return abs(y - t) / len(t)

def mean_rel_error(y, t):
    """Return the relative mean error between y and t."""
    return abs((y - t) / t) / len(t)


def tanh(x):
    """Numerically stable tanh function.

    Parameters
    ----------
    x : float or array_like of floats
        The input values to compute tanh.

    Returns
    -------
    float or array_like of floats
        The tanh value of `x`.
    """
    if isinstance(x, np.ndarray):
        return np.tanh(x)
    else:
        if x >= 0:
            return np.exp(-x) / (1 + np.exp(-x))
        else:
            return -np.exp(x) / (1 + np.exp(x))

def sigmoid(z):
    """Compute the sigmoid of z.

    Parameters
    ----------
    z : float or array_like of floats
        The value(s) to compute sigmoid.

    Returns
    -------
    float or array_like of floats
        The value of the sigmoid at `z` computed numerically.
    """
    if isinstance(z, np.ndarray):
        return 1 / (1 + np.exp((-1)*z))
    else:
        return 1 / (1 + np.exp((-1)*z))


def softmax(z):
    """Compute the softmax of z.

    Parameters
    ----------
    z : array_like
        A list of numbers to be softmaxed.

    Returns
    -------
    array_like
        The result of softmaxing each element in z.
    """
    return np.exp(z) / np.sum(np.exp(z), axis=0)