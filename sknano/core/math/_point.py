# -*- coding: utf-8 -*-
"""
==============================================================================
Custom NumPy Point class (:mod:`sknano.core.math._point`)
==============================================================================

.. currentmodule:: sknano.core.math._point

"""
from __future__ import absolute_import, division, print_function
__docformat__ = 'restructuredtext en'

import numbers
import numpy as np

__all__ = ['Point']


class Point(np.ndarray):
    """Abstract object representation of a point in :math:`R^n`

    Parameters
    ----------
    p : array_like, optional
        :math:`x, y` coordinates of point in :math:`R^2` space.
        :math:`x, y, z` coordinates of point in :math:`R^3` space.
    nd : {None, int}, optional
    dtype : data-type, optional
    copy : bool, optional

    """
    __array_priority__ = 10.0

    def __new__(cls, p=None, nd=None, dtype=None, copy=True, verbose=False):

        if isinstance(p, Point):
            if dtype is None:
                intype = p.dtype
            else:
                intype = np.dtype(dtype)

            pt = p.view(cls)
            if intype != p.dtype:
                return pt.astype(intype)

            if copy:
                return pt.copy()
            else:
                return pt

        dtype = np.dtype(dtype)

        if isinstance(p, (tuple, list, np.ndarray)):
            try:
                for i, coord in enumerate(p[:]):
                    if coord is None:
                        p[i] = 0.0
            except TypeError:
                p = np.zeros(len(p), dtype=dtype)
            else:
                p = np.asarray(p, dtype=dtype)
            nd = len(p)
        else:
            if nd is None or not isinstance(nd, numbers.Number):
                nd = 3
            else:
                nd = int(nd)
            p = np.zeros(nd, dtype=dtype)

        arr = np.array(p, dtype=dtype, copy=copy).view(cls)
        pt = np.ndarray.__new__(cls, arr.shape, arr.dtype, buffer=arr)
        #pt = super(Point, cls).__new__(cls, arr.shape, arr.dtype, buffer=arr)

        pt.nd = nd
        if nd == 2:
            pt.x, pt.y = pt
        elif nd == 3:
            pt.x, pt.y, pt.z = pt

        return pt

    def __array_finalize__(self, pt):

        if pt is None:
            return None

        self.nd = len(pt)

        if self.nd == 2:
            self.x, self.y = pt
        elif self.nd == 3:
            self.x, self.y, self.z = pt

    def __str__(self):
        return repr(self)

    def __repr__(self):
        reprstr = "Point({p!r}, nd={nd!r}, dtype={dtype!r})"
        parameters = dict(p=self.__array__(),
                          nd=getattr(self, 'nd', None),
                          dtype=self.dtype)
        return reprstr.format(**parameters)

    def __getattr__(self, name):
        try:
            nd = len(self)
            if nd == 2 and name in ('x', 'y'):
                if name == 'x':
                    return self[0]
                else:
                    return self[1]
            elif nd == 3 and name in ('x', 'y', 'z'):
                if name == 'x':
                    return self[0]
                elif name == 'y':
                    return self[1]
                else:
                    return self[2]
        except TypeError:
            pass
        return super(Point, self).__getattribute__(name)

    def __setattr__(self, name, value):
        #nd = len(self)
        nd = getattr(self, 'nd', None)
        if nd is not None and nd == 2 and name in ('x', 'y'):
            if name == 'x':
                self[0] = value
            else:
                self[1] = value
        elif nd is not None and nd == 3 and name in ('x', 'y', 'z'):
            if name == 'x':
                self[0] = value
            elif name == 'y':
                self[1] = value
            else:
                self[2] = value
        else:
            super(Point, self).__setattr__(name, value)

    def rezero_coords(self, epsilon=1.0e-10):
        """Re-zero `Point` coordinates near zero.

        Set `Point` coordinates with absolute value less than `epsilon` to
        zero.

        Parameters
        ----------
        epsilon : float, optional
            Smallest allowed absolute value of any :math:`x,y,z` coordinate.

        """
        self[np.where(np.abs(self) <= epsilon)] = 0.0