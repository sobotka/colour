# -*- coding: utf-8 -*-
"""
CIE L*a*b* Colourspace
======================

Defines the *CIE L\\*a\\*b\\** colourspace transformations:

-   :func:`colour.XYZ_to_Lab`
-   :func:`colour.Lab_to_XYZ`
-   :func:`colour.Lab_to_LCHab`
-   :func:`colour.LCHab_to_Lab`

See Also
--------
`CIE L*a*b* Colourspace Jupyter Notebook
<http://nbviewer.jupyter.org/github/colour-science/colour-notebooks/\
blob/master/notebooks/models/cie_lab.ipynb>`_

References
----------
-   :cite:`CIETC1-482004m` : CIE TC 1-48. (2004). CIE 1976 uniform colour
    spaces. In CIE 015:2004 Colorimetry, 3rd Edition (p. 24).
    ISBN:978-3-901-90633-6
"""

from __future__ import division, unicode_literals

import numpy as np

from colour.algebra import cartesian_to_polar, polar_to_cartesian
from colour.colorimetry import (ILLUMINANTS,
                                intermediate_lightness_function_CIE1976,
                                intermediate_luminance_function_CIE1976)
from colour.models import xy_to_xyY, xyY_to_XYZ
from colour.utilities import (from_range_1, from_range_100, from_range_degrees,
                              to_domain_1, to_domain_100, to_domain_degrees,
                              tsplit, tstack)

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2019 - Colour Developers'
__license__ = 'New BSD License - https://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['XYZ_to_Lab', 'Lab_to_XYZ', 'Lab_to_LCHab', 'LCHab_to_Lab']


def XYZ_to_Lab(
        XYZ,
        illuminant=ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['D65']):
    """
    Converts from *CIE XYZ* tristimulus values to *CIE L\\*a\\*b\\**
    colourspace.

    Parameters
    ----------
    XYZ : array_like
        *CIE XYZ* tristimulus values.
    illuminant : array_like, optional
        Reference *illuminant* *CIE xy* chromaticity coordinates or *CIE xyY*
        colourspace array.

    Returns
    -------
    ndarray
        *CIE L\\*a\\*b\\** colourspace array.

    Notes
    -----

    +----------------+-----------------------+-----------------+
    | **Domain**     | **Scale - Reference** | **Scale - 1**   |
    +================+=======================+=================+
    | ``XYZ``        | [0, 1]                | [0, 1]          |
    +----------------+-----------------------+-----------------+
    | ``illuminant`` | [0, 1]                | [0, 1]          |
    +----------------+-----------------------+-----------------+

    +----------------+-----------------------+-----------------+
    | **Range**      | **Scale - Reference** | **Scale - 1**   |
    +================+=======================+=================+
    | ``Lab``        | ``L`` : [0, 100]      | ``L`` : [0, 1]  |
    |                |                       |                 |
    |                | ``a`` : [-100, 100]   | ``a`` : [-1, 1] |
    |                |                       |                 |
    |                | ``b`` : [-100, 100]   | ``b`` : [-1, 1] |
    +----------------+-----------------------+-----------------+

    References
    ----------
    :cite:`CIETC1-482004m`

    Examples
    --------
    >>> XYZ = np.array([0.20654008, 0.12197225, 0.05136952])
    >>> XYZ_to_Lab(XYZ)  # doctest: +ELLIPSIS
    array([ 41.5278752...,  52.6385830...,  26.9231792...])
    """

    X, Y, Z = tsplit(to_domain_1(XYZ))

    X_n, Y_n, Z_n = tsplit(xyY_to_XYZ(xy_to_xyY(illuminant)))

    f_X_X_n = intermediate_lightness_function_CIE1976(X, X_n)
    f_Y_Y_n = intermediate_lightness_function_CIE1976(Y, Y_n)
    f_Z_Z_n = intermediate_lightness_function_CIE1976(Z, Z_n)

    L = 116 * f_Y_Y_n - 16
    a = 500 * (f_X_X_n - f_Y_Y_n)
    b = 200 * (f_Y_Y_n - f_Z_Z_n)

    Lab = tstack([L, a, b])

    return from_range_100(Lab)


def Lab_to_XYZ(
        Lab,
        illuminant=ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['D65']):
    """
    Converts from *CIE L\\*a\\*b\\** colourspace to *CIE XYZ* tristimulus
    values.

    Parameters
    ----------
    Lab : array_like
        *CIE L\\*a\\*b\\** colourspace array.
    illuminant : array_like, optional
        Reference *illuminant* *CIE xy* chromaticity coordinates or *CIE xyY*
        colourspace array.

    Returns
    -------
    ndarray
        *CIE XYZ* tristimulus values.

    Notes
    -----

    +----------------+-----------------------+-----------------+
    | **Domain**     | **Scale - Reference** | **Scale - 1**   |
    +================+=======================+=================+
    | ``Lab``        | ``L`` : [0, 100]      | ``L`` : [0, 1]  |
    |                |                       |                 |
    |                | ``a`` : [-100, 100]   | ``a`` : [-1, 1] |
    |                |                       |                 |
    |                | ``b`` : [-100, 100]   | ``b`` : [-1, 1] |
    +----------------+-----------------------+-----------------+
    | ``illuminant`` | [0, 1]                | [0, 1]          |
    +----------------+-----------------------+-----------------+

    +----------------+-----------------------+-----------------+
    | **Range**      | **Scale - Reference** | **Scale - 1**   |
    +================+=======================+=================+
    | ``XYZ``        | [0, 1]                | [0, 1]          |
    +----------------+-----------------------+-----------------+

    References
    ----------
    :cite:`CIETC1-482004m`

    Examples
    --------
    >>> Lab = np.array([41.52787529, 52.63858304, 26.92317922])
    >>> Lab_to_XYZ(Lab)  # doctest: +ELLIPSIS
    array([ 0.2065400...,  0.1219722...,  0.0513695...])
    """

    L, a, b = tsplit(to_domain_100(Lab))

    X_n, Y_n, Z_n = tsplit(xyY_to_XYZ(xy_to_xyY(illuminant)))

    f_Y_Y_n = (L + 16) / 116
    f_X_X_n = a / 500 + f_Y_Y_n
    f_Z_Z_n = f_Y_Y_n - b / 200

    X = intermediate_luminance_function_CIE1976(f_X_X_n, X_n)
    Y = intermediate_luminance_function_CIE1976(f_Y_Y_n, Y_n)
    Z = intermediate_luminance_function_CIE1976(f_Z_Z_n, Z_n)

    XYZ = tstack([X, Y, Z])

    return from_range_1(XYZ)


def Lab_to_LCHab(Lab):
    """
    Converts from *CIE L\\*a\\*b\\** colourspace to *CIE L\\*C\\*Hab*
    colourspace.

    Parameters
    ----------
    Lab : array_like
        *CIE L\\*a\\*b\\** colourspace array.

    Returns
    -------
    ndarray
        *CIE L\\*C\\*Hab* colourspace array.

    Notes
    -----

    +------------+-----------------------+-----------------+
    | **Domain** | **Scale - Reference** | **Scale - 1**   |
    +============+=======================+=================+
    | ``Lab``    | ``L`` : [0, 100]      | ``L`` : [0, 1]  |
    |            |                       |                 |
    |            | ``a`` : [-100, 100]   | ``a`` : [-1, 1] |
    |            |                       |                 |
    |            | ``b`` : [-100, 100]   | ``b`` : [-1, 1] |
    +------------+-----------------------+-----------------+

    +------------+-----------------------+-----------------+
    | **Range**  | **Scale - Reference** | **Scale - 1**   |
    +============+=======================+=================+
    | ``LCHab``  | ``L``  : [0, 100]     | ``L``  : [0, 1] |
    |            |                       |                 |
    |            | ``C``  : [0, 100]     | ``C``  : [0, 1] |
    |            |                       |                 |
    |            | ``ab`` : [0, 360]     | ``ab`` : [0, 1] |
    +------------+-----------------------+-----------------+

    References
    ----------
    :cite:`CIETC1-482004m`

    Examples
    --------
    >>> Lab = np.array([41.52787529, 52.63858304, 26.92317922])
    >>> Lab_to_LCHab(Lab)  # doctest: +ELLIPSIS
    array([ 41.5278752...,  59.1242590...,  27.0884878...])
    """

    L, a, b = tsplit(Lab)

    C, H = tsplit(cartesian_to_polar(tstack([a, b])))

    LCHab = tstack([L, C, from_range_degrees(np.degrees(H) % 360)])

    return LCHab


def LCHab_to_Lab(LCHab):
    """
    Converts from *CIE L\\*C\\*Hab* colourspace to *CIE L\\*a\\*b\\**
    colourspace.

    Parameters
    ----------
    LCHab : array_like
        *CIE L\\*C\\*Hab* colourspace array.

    Returns
    -------
    ndarray
        *CIE L\\*a\\*b\\** colourspace array.

    Notes
    -----

    +-------------+-----------------------+-----------------+
    | **Domain**  | **Scale - Reference** | **Scale - 1**   |
    +=============+=======================+=================+
    | ``LCHab``   | ``L``  : [0, 100]     | ``L``  : [0, 1] |
    |             |                       |                 |
    |             | ``C``  : [0, 100]     | ``C``  : [0, 1] |
    |             |                       |                 |
    |             | ``ab`` : [0, 360]     | ``ab`` : [0, 1] |
    +-------------+-----------------------+-----------------+

    +-------------+-----------------------+-----------------+
    | **Range**   | **Scale - Reference** | **Scale - 1**   |
    +=============+=======================+=================+
    | ``Lab``     | ``L`` : [0, 100]      | ``L`` : [0, 1]  |
    |             |                       |                 |
    |             | ``a`` : [-100, 100]   | ``a`` : [-1, 1] |
    |             |                       |                 |
    |             | ``b`` : [-100, 100]   | ``b`` : [-1, 1] |
    +-------------+-----------------------+-----------------+

    References
    ----------
    :cite:`CIETC1-482004m`

    Examples
    --------
    >>> LCHab = np.array([41.52787529, 59.12425901, 27.08848784])
    >>> LCHab_to_Lab(LCHab)  # doctest: +ELLIPSIS
    array([ 41.5278752...,  52.6385830...,  26.9231792...])
    """

    L, C, H = tsplit(LCHab)

    a, b = tsplit(
        polar_to_cartesian(tstack([C, np.radians(to_domain_degrees(H))])))

    Lab = tstack([L, a, b])

    return Lab
