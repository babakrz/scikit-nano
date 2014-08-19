# -*- coding: utf-8 -*-
"""
==================================================================
Custom NumPy data structures (:mod:`sknano.core._npcoremath`)
==================================================================

.. currentmodule:: sknano.core._npcoremath

"""
from __future__ import absolute_import, division, print_function
__docformat__ = 'restructuredtext en'

import numbers
import numpy as np

__all__ = ['Point', 'Vector']


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

    def __new__(cls, p=None, nd=None, dtype=None, copy=True):

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
        pt = super(Point, cls).__new__(cls, arr.shape, arr.dtype,
                                       buffer=arr)

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

    def __repr__(self):
        return np.array(self).__repr__()

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


class Vector(np.ndarray):
    """Abstract object representation of a vector in :math:`R^n`

    Parameters
    ----------
    v : array_like, optional
        components of vector
    nd : {None, int}, optional
    p : array_like, optional
        Terminating `Point` of vector.
        :math:`x, y` coordinates of point in :math:`R^2` space.
        :math:`x, y, z` coordinates of point in :math:`R^3` space.
    p0 : array_like, optional
        Origin `Point` of vector in :math:`R^n` space.
    dtype : data-type, optional
    copy : bool, optional

    Notes
    -----
    .. todo::

       add new methods for coordinate transformations

    """
    __array_priority__ = 10.0

    def __new__(cls, v=None, nd=None, p=None, p0=None, dtype=None, copy=True):

        if isinstance(v, Vector):
            if dtype is None:
                intype = v.dtype
            else:
                intype = np.dtype(dtype)

            vec = v.view(cls)
            if intype != v.dtype:
                return vec.astype(intype)

            if copy:
                return vec.copy()
            else:
                return vec

        if isinstance(v, (tuple, list, np.ndarray)):
            v = np.asarray(v)
            nd = len(v)

            if p0 is None:
                p0 = Point(nd=nd, dtype=dtype)
            else:
                p0 = Point(p0, nd=nd, dtype=dtype)
            p = p0 + v
        else:
            if nd is None or not isinstance(nd, numbers.Number):
                nd = 3
            if p is None:
                p = Point(nd=nd, dtype=dtype)
            else:
                p = Point(p, nd=nd, dtype=dtype)

            if p0 is None:
                p0 = Point(nd=nd, dtype=dtype)
            else:
                p0 = Point(p0, nd=nd, dtype=dtype)

            v = p - p0

        arr = np.array(v, dtype=dtype, copy=copy).view(cls)
        vec = super(Vector, cls).__new__(cls, arr.shape, arr.dtype,
                                         buffer=arr)

        vec.nd = nd
        vec._p = p
        vec._p0 = p0
        if nd == 2:
            vec.x, vec.y = vec
        elif nd == 3:
            vec.x, vec.y, vec.z = vec

        return vec

    def __array_finalize__(self, vec):
        if vec is None:
            return None

        #print('In __array_finalize__\n' +
        #      'type(self): {}\n'.format(type(self)) +
        #      'type(vec): {}\n'.format(type(vec)) +
        #      'vec: {}\n'.format(vec))

        self.nd = len(vec)

        if self.nd == 2:
            self.x, self.y = vec
        elif self.nd == 3:
            self.x, self.y, self.z = vec

        self._p = getattr(vec, 'p', None)
        self._p0 = getattr(vec, 'p0', None)

    def __repr__(self):
        return np.array(self).__repr__()

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
        return super(Vector, self).__getattribute__(name)

    def __setattr__(self, name, value):
        #nd = len(self)
        nd = getattr(self, 'nd', None)
        if nd is not None and nd == 2 and name in ('x', 'y'):
            if name == 'x':
                self[0] = value
                try:
                    self._p.x = self._p0.x + value
                except AttributeError:
                    pass
            else:
                self[1] = value
                try:
                    self._p.y = self._p0.y + value
                except AttributeError:
                    pass
        elif nd is not None and nd == 3 and name in ('x', 'y', 'z'):
            if name == 'x':
                self[0] = value
                try:
                    self._p.x = self._p0.x + value
                except AttributeError:
                    pass
            elif name == 'y':
                self[1] = value
                try:
                    self._p.y = self._p0.y + value
                except AttributeError:
                    pass
            else:
                self[2] = value
                try:
                    self._p.z = self._p0.z + value
                except AttributeError:
                    pass
        else:
            super(Vector, self).__setattr__(name, value)

    @property
    def p(self):
        """Terminating :class:`Point` of vector."""
        return self._p

    @p.setter
    def p(self, value=np.ndarray):
        """Set new terminating :class:`Point` of vector."""
        self._p[:] = value
        self[:] = self._p - self._p0

    @property
    def p0(self):
        """Origin :class:`Point` of vector."""
        return self._p0

    @p0.setter
    def p0(self, value=np.ndarray):
        """Set new origin :class:`Point` of vector."""
        self._p0[:] = value
        self[:] = self._p - self._p0

    def rezero_components(self, epsilon=1.0e-10):
        """Re-zero `Vector` coordinates near zero.

        Set `Vector` coordinates with absolute value less than `epsilon` to
        zero.

        Parameters
        ----------
        epsilon : float, optional
            Smallest allowed absolute value of any :math:`x,y,z` coordinate.

        """
        self[np.where(np.abs(self) <= epsilon)] = 0.0
