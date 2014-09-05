# -*- coding: utf-8 -*-
"""
===============================================================================
Nanotube structure generators (:mod:`sknano.generators._swnt_generator`)
===============================================================================

.. currentmodule:: sknano.generators._swnt_generator

.. todo::

   Add methods to perform fractional translation and cartesian translation
   before structure generation.

.. todo::

   Handle different units in output coordinates.

"""
from __future__ import absolute_import, division, print_function
__docformat__ = 'restructuredtext en'

import numpy as np

from sknano.core import pluralize
from sknano.core.math import Vector
from sknano.structures import SWNT, compute_chiral_angle
from sknano.utils.geometric_shapes import Cuboid
from ._base import GeneratorAtom as Atom, GeneratorAtoms as Atoms, \
    GeneratorMixin

__all__ = ['SWNTGenerator']


class SWNTGenerator(SWNT, GeneratorMixin):
    u"""Class for generating nanotube structures.

    Parameters
    ----------
    n, m : int
        Chiral indices defining the nanotube chiral vector
        :math:`\\mathbf{C}_{h} = n\\mathbf{a}_{1} + m\\mathbf{a}_{2} = (n, m)`.
    nz : int, optional
        Number of repeat unit cells in the :math:`z` direction, along
        the *length* of the nanotube.
    element1, element2 : {str, int}, optional
        Element symbol or atomic number of basis
        :class:`~sknano.core.Atom` 1 and 2
    bond : float, optional
        :math:`\\mathrm{a}_{\\mathrm{CC}} =` distance between
        nearest neighbor atoms. Must be in units of **Angstroms**.
    Lz : float, optional
        Length of nanotube in units of **nanometers**.
        Overrides the `nz` value.

        .. versionadded:: 0.2.5

    tube_length : float, optional
        Length of nanotube in units of **nanometers**.
        Overrides the `nz` value.

        .. deprecated:: 0.2.5
           Use `Lz` instead

    fix_Lz : bool, optional
        Generate the nanotube with length as close to the specified
        :math:`L_z` as possible. If `True`, then
        non integer :math:`n_z` cells are permitted.

        .. versionadded:: 0.2.6

    autogen : bool, optional
        if `True`, automatically call
        :meth:`~SWNTGenerator.generate_unit_cell`,
        followed by :meth:`~SWNTGenerator.generate_structure_data`.
    verbose : bool, optional
        if `True`, show verbose output

    Examples
    --------
    First, load the :class:`~sknano.generators.SWNTGenerator` class.

    >>> from sknano.generators import SWNTGenerator

    Now let's generate a :math:`\\mathbf{C}_{\\mathrm{h}} = (10, 5)`
    SWCNT unit cell.

    >>> nt = SWNTGenerator(n=10, m=5)
    >>> nt.save_data(fname='10,5_unit_cell.xyz')

    The rendered structure looks like (orhographic view):

    .. image:: /images/10,5_unit_cell_orthographic_view.png

    and the perspective view:

    .. image:: /images/10,5_unit_cell_perspective_view.png

    """
    def __init__(self, autogen=True, **kwargs):

        super(SWNTGenerator, self).__init__(**kwargs)

        if autogen:
            self.generate_unit_cell()
            self.generate_structure_data()

    def generate_unit_cell(self):
        """Generate the nanotube unit cell."""
        eps = 0.01
        n = self.n
        m = self.m
        bond = self.bond
        M = self.M
        T = self.T
        N = self.N
        rt = self.rt
        e1 = self.element1
        e2 = self.element2
        verbose = self._verbose

        aCh = compute_chiral_angle(n=n, m=m, rad2deg=False)

        tau = M * T / N
        dtau = bond * np.sin(np.pi / 6 - aCh)

        psi = 2 * np.pi / N
        dpsi = bond * np.cos(np.pi / 6 - aCh) / rt

        if verbose:
            print('dpsi: {}'.format(dpsi))
            print('dtau: {}\n'.format(dtau))

        self._unit_cell = Atoms()

        for i in xrange(1, N + 1):
            x1 = rt * np.cos(i * psi)
            y1 = rt * np.sin(i * psi)
            z1 = i * tau

            while z1 > T - eps:
                z1 -= T

            atom1 = Atom(element=e1, x=x1, y=y1, z=z1)
            atom1.rezero()

            if verbose:
                print('Basis Atom 1:\n{}'.format(atom1))

            self.unit_cell.append(atom1)

            x2 = rt * np.cos(i * psi + dpsi)
            y2 = rt * np.sin(i * psi + dpsi)
            z2 = i * tau - dtau
            while z2 > T - eps:
                z2 -= T

            atom2 = Atom(element=e2, x=x2, y=y2, z=z2)
            atom2.rezero()

            if verbose:
                print('Basis Atom 2:\n{}'.format(atom2))

            self.unit_cell.append(atom2)

    def generate_structure_data(self):
        """Generate structure data."""
        self.structure_atoms = Atoms()
        for nz in xrange(int(np.ceil(self.nz))):
            dr = Vector([0.0, 0.0, nz * self.T])
            for uc_atom in self.unit_cell:
                nt_atom = Atom(element=uc_atom.symbol)
                nt_atom.r = uc_atom.r + dr
                self.structure_atoms.append(nt_atom)

    def save_data(self, fname=None, outpath=None, structure_format=None,
                  rotation_angle=None, rot_axis=None, anchor_point=None,
                  deg2rad=True, center_CM=True, savecopy=True, **kwargs):
        """Save structure data.

        See :meth:`~sknano.generators.GeneratorMixin.save_data` method
        for documentation.

        """
        if fname is None:
            chirality = '{}{}r'.format('{}'.format(self.n).zfill(2),
                                       '{}'.format(self.m).zfill(2))
            if self._assume_integer_unit_cells:
                nz = ''.join(('{}'.format(self.nz),
                              pluralize('cell', self.nz)))
            else:
                nz = ''.join(('{:.2f}'.format(self.nz),
                              pluralize('cell', self.nz)))
            fname_wordlist = (chirality, nz)
            fname = '_'.join(fname_wordlist)

        if self._L0 is not None and self._fix_Lz:
            pmin = [-np.inf, -np.inf, 0]
            pmax = [np.inf, np.inf, 10 * self._L0 + 0.25]
            region_bounds = Cuboid(pmin=pmin, pmax=pmax)
            region_bounds.update_region_limits()

            self.structure_atoms.clip_bounds(region_bounds,
                                             center_before_clipping=True)

        if center_CM:
            self.structure_atoms.center_CM()

        super(SWNTGenerator, self).save_data(
            fname=fname, outpath=outpath, structure_format=structure_format,
            rotation_angle=rotation_angle, rot_axis=rot_axis,
            anchor_point=anchor_point, deg2rad=deg2rad, center_CM=False,
            savecopy=savecopy, **kwargs)
