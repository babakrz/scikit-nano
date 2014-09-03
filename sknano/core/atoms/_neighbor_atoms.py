# -*- coding: utf-8 -*-
"""
===============================================================================
Class container for neighbor atoms (:mod:`sknano.core.atoms._neighbor_atoms`)
===============================================================================

.. currentmodule:: sknano.core.atoms._neighbor_atoms

"""
from __future__ import absolute_import, division, print_function
__docformat__ = 'restructuredtext en'

#import numpy as np

from ._base import AtomList

__all__ = ['NeighborAtoms']


class NeighborAtoms(AtomList):
    """An eXtended `Atoms` class for structure analysis.

    Parameters
    ----------
    atoms : {None, sequence, `NeighborAtoms`}, optional
        if not `None`, then a list of `XAtom` instance objects or an
        existing `NeighborAtoms` instance object.
    copylist : bool, optional
        perform shallow copy of atoms list
    deepcopy : bool, optional
        perform deepcopy of atoms list

    """

    def __init__(self, atoms=None, copylist=True, deepcopy=False):
        super(NeighborAtoms, self).__init__(atoms=atoms, copylist=copylist,
                                            deepcopy=deepcopy)

    def __str__(self):
        """Return a nice string representation of `NeighborAtoms`."""
        return "NeighborAtoms(atoms={!s})".format(self._data)

    def __repr__(self):
        """Return the canonical string representation of `NeighborAtoms`."""
        return "NeighborAtoms(atoms={!r})".format(self._data)

    @property
    def NNN(self):
        return len(self)