# -*- coding: utf-8 -*-
"""
Sony .spi1d LUT Format Input / Output Utilities
===============================================

Defines *Sony* *.spi1d* *LUT* Format related input / output utilities objects.

-   :func:`colour.io.read_LUT_SonySPI1D`
-   :func:`colour.io.write_LUT_SonySPI1D`
"""

from __future__ import division, unicode_literals

import numpy as np

from colour.constants import DEFAULT_INT_DTYPE
from colour.io.luts import LUT1D, LUT3x1D, LUTSequence
from colour.io.luts.common import parse_array, path_to_title
from colour.utilities import as_float_array, usage_warning

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2019 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['read_LUT_SonySPI1D', 'write_LUT_SonySPI1D']


def read_LUT_SonySPI1D(path):
    """
    Reads given *Sony* *.spi1d* *LUT* file.

    Parameters
    ----------
    path : unicode
        *LUT* path.

    Returns
    -------
    LUT1D or LUT3x1D
        :class:`LUT1D` or :class:`LUT3x1D` class instance.

    Examples
    --------
    Reading a 1D *Sony* *.spi1d* *LUT*:

    >>> import os
    >>> path = os.path.join(
    ...     os.path.dirname(__file__), 'tests', 'resources', 'sony_spi1d',
    ...     'oetf_reverse_sRGB_1D.spi1d')
    >>> print(read_LUT_SonySPI1D(path))
    LUT1D - oetf reverse sRGB 1D
    ----------------------------
    <BLANKLINE>
    Dimensions : 1
    Domain     : [-0.1  1.5]
    Size       : (16,)
    Comment 01 : Generated by "Colour 0.3.11".
    Comment 02 : "colour.models.oetf_reverse_sRGB".

    Reading a 3x1D *Sony* *.spi1d* *LUT*:

    >>> path = os.path.join(
    ...     os.path.dirname(__file__), 'tests', 'resources', 'sony_spi1d',
    ...     'oetf_reverse_sRGB_3x1D.spi1d')
    >>> print(read_LUT_SonySPI1D(path))
    LUT3x1D - oetf reverse sRGB 3x1D
    --------------------------------
    <BLANKLINE>
    Dimensions : 2
    Domain     : [[-0.1 -0.1 -0.1]
                  [ 1.5  1.5  1.5]]
    Size       : (16, 3)
    Comment 01 : Generated by "Colour 0.3.11".
    Comment 02 : "colour.models.oetf_reverse_sRGB".
    """

    title = path_to_title(path)
    domain_min, domain_max = np.array([0, 1])
    dimensions = 1
    table = []

    comments = []

    with open(path) as spi1d_file:
        lines = spi1d_file.readlines()
        for line in lines:
            line = line.strip()

            if len(line) == 0:
                continue

            if line.startswith('#'):
                comments.append(line[1:].strip())
                continue

            tokens = line.split()
            if tokens[0] == 'Version':
                continue
            if tokens[0] == 'From':
                domain_min, domain_max = parse_array(tokens[1:])
            elif tokens[0] == 'Length':
                continue
            elif tokens[0] == 'Components':
                component = DEFAULT_INT_DTYPE(tokens[1])
                assert component in (1, 3), (
                    'Only 1 or 3 components are supported!')

                dimensions = 1 if component == 1 else 2
            elif tokens[0] in ('{', '}'):
                continue
            else:
                table.append(parse_array(tokens))

    table = as_float_array(table)
    if dimensions == 1:
        return LUT1D(
            np.squeeze(table),
            title,
            np.array([domain_min, domain_max]),
            comments=comments)
    elif dimensions == 2:
        return LUT3x1D(
            table,
            title,
            np.array([[domain_min, domain_min, domain_min],
                      [domain_max, domain_max, domain_max]]),
            comments=comments)


def write_LUT_SonySPI1D(LUT, path, decimals=7):
    """
    Writes given *LUT* to given *Sony* *.spi1d* *LUT* file.

    Parameters
    ----------
    LUT : LUT1D or LUT2d
        :class:`LUT1D`, :class:`LUT3x1D` or :class:`LUTSequence` class instance
        to write at given path.
    path : unicode
        *LUT* path.
    decimals : int, optional
        Formatting decimals.

    Returns
    -------
    bool
        Definition success.

    Warning
    -------
    -   If a :class:`LUTSequence` class instance is passed as ``LUT``, the
        first *LUT* in the *LUT* sequence will be used.

    Examples
    --------
    Writing a 1D *Sony* *.spi1d* *LUT*:

    >>> from colour.algebra import spow
    >>> domain = np.array([-0.1, 1.5])
    >>> LUT = LUT1D(
    ...     spow(LUT1D.linear_table(16), 1 / 2.2),
    ...     'My LUT',
    ...     domain,
    ...     comments=['A first comment.', 'A second comment.'])
    >>> write_LUT_SonySPI1D(LUT, 'My_LUT.cube')  # doctest: +SKIP

    Writing a 3x1D *Sony* *.spi1d* *LUT*:

    >>> domain = np.array([[-0.1, -0.1, -0.1], [1.5, 1.5, 1.5]])
    >>> LUT = LUT3x1D(
    ...     spow(LUT3x1D.linear_table(16), 1 / 2.2),
    ...     'My LUT',
    ...     domain,
    ...     comments=['A first comment.', 'A second comment.'])
    >>> write_LUT_SonySPI1D(LUT, 'My_LUT.cube')  # doctest: +SKIP
    """

    if isinstance(LUT, LUTSequence):
        LUT = LUT[0]
        usage_warning('"LUT" is a "LUTSequence" instance was passed, '
                      'using first sequence "LUT":\n'
                      '{0}'.format(LUT))

    assert not LUT.is_domain_explicit(), '"LUT" domain must be implicit!'

    assert (isinstance(LUT, LUT1D) or isinstance(
        LUT, LUT3x1D)), ('"LUT" must be either a 1D or 3x1D "LUT"!')

    is_1D = isinstance(LUT, LUT1D)

    if is_1D:
        domain = LUT.domain
    else:
        domain = np.unique(LUT.domain)

        assert len(domain) == 2, 'Non-uniform "LUT" domain is unsupported!'

    def _format_array(array):
        """
        Formats given array as a *Sony* *.spi1d* data row.
        """

        return ' {1:0.{0}f} {2:0.{0}f} {3:0.{0}f}'.format(decimals, *array)

    with open(path, 'w') as spi1d_file:
        spi1d_file.write('Version 1\n')

        spi1d_file.write('From {1:0.{0}f} {2:0.{0}f}\n'.format(
            decimals, *domain))

        spi1d_file.write('Length {0}\n'.format(LUT.table.size if is_1D else
                                               LUT.table.shape[0]))

        spi1d_file.write('Components {0}\n'.format(1 if is_1D else 3))

        spi1d_file.write('{\n')
        for row in LUT.table:
            if is_1D:
                spi1d_file.write(' {1:0.{0}f}\n'.format(decimals, row))
            else:
                spi1d_file.write('{0}\n'.format(_format_array(row)))
        spi1d_file.write('}\n')

        if LUT.comments:
            for comment in LUT.comments:
                spi1d_file.write('# {0}\n'.format(comment))

    return True
