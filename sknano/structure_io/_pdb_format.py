# -*- coding: utf-8 -*-
"""
====================================================
PDB format (:mod:`sknano.structure_io._pdb_format`)
====================================================

.. currentmodule:: sknano.structure_io._pdb_format

"""
from __future__ import absolute_import, division, print_function
__docformat__ = 'restructuredtext en'

from collections import OrderedDict

from ..chemistry import Atom, Atoms
from ..tools import get_fpath

from ._structure_data import StructureReader, StructureReaderError, \
    StructureWriter, StructureFormat, default_comment_line

__all__ = ['PDBData', 'PDBReader', 'PDBWriter', 'PDBFormat']


class PDBReader(StructureReader):
    """Class for reading pdb chemical file format.

    Parameters
    ----------
    fpath : str
        pdb structure file

    """
    def __init__(self, fpath=None):
        super(PDBReader, self).__init__(fpath=fpath)

        if fpath is not None:
            self.read()

    def read(self):
        """Read PDB file."""
        with open(self.fpath, 'r') as f:
            lines = f.readlines()
            for line in lines:
                print(line)


class PDBWriter(StructureWriter):
    """Class for writing pdb chemical file format."""

    @classmethod
    def write(cls, fname=None, outpath=None, atoms=None, comment_line=None):
        """Write structure data to file.

        Parameters
        ----------
        fname : str
        outpath : str, optional
            Output path for structure data file.
        atoms : :py:class:`~sknano.chemistry.Atoms`
            An :py:class:`~sknano.chemistry.Atoms` instance.
        comment_line : str, optional

        """
        if not isinstance(atoms, Atoms):
            raise TypeError('atoms argument must be an `Atoms` instance')
        else:
            fpath = get_fpath(fname=fname, ext='pdb', outpath=outpath,
                              overwrite=True, add_fnum=False)
            if comment_line is None:
                comment_line = default_comment_line

            atoms.rezero_coords()

            with open(fpath, 'w') as f:
                f.write('{:d}\n'.format(atoms.Natoms))
                f.write('{}\n'.format(comment_line))
                for atom in atoms:
                    f.write('{:>3s}{:15.8f}{:15.8f}{:15.8f}\n'.format(
                        atom.symbol, atom.x, atom.y, atom.z))


class PDBData(PDBReader):
    """Class for reading and writing structure data in PDB data format.

    Parameters
    ----------
    fpath : str, optional

    """
    def __init__(self, fpath=None):
        try:
            super(PDBData, self).__init__(fpath=fpath)
        except StructureReaderError:
            pass

    def write(self, pdbfile=None):
        pass


class PDBFormat(StructureFormat):
    """Class defining the structure file format for PDB data.

    Parameters
    ----------

    """
    def __init__(self):
        super(PDBFormat, self).__init__()

        self._records = OrderedDict()
        #self._records['HEADER'] = header = {}
        #self._records['TITLE'] = title = {}
        #self._records['MASTER'] = {}
        self._records['ATOM'] = atom = {}
        atom['format'] = \
            '{:6}{:>5} {:>4}{:1}{:>3} {:1}{:>4}{:1}' + \
            '{:3}'.format('') + \
            '{:>8.3f}{:>8.3f}{:>8.3f}' + \
            '{:>6.2f}{:>6.2f}' + \
            '{:10}'.format('') + \
            '{:2}{:2}'
        self._records['CONECT'] = {}
        self._records['END'] = None

        self._properties['RECORDS'] = self._records

    @property
    def records(self):
        return self._records
