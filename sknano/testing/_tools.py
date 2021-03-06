# -*- coding: utf-8 -*-
"""
========================================================================
Test fixtures (:mod:`sknano.testing._tools`)
========================================================================

.. currentmodule:: sknano.testing._tools

"""
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

from ._funcs import generate_atoms

__all__ = ['GeneratorTestFixtures', 'AtomsTestFixture']


import os
import unittest


class GeneratorTestFixtures(unittest.TestCase):
    """Mixin unittest.TestCase class defining setUp/tearDown methods to
    keep track of and delete the structure data files generated by the
    sknano.generators classes."""

    def setUp(self):
        self.tmpdata = []

    def tearDown(self):
        for f in self.tmpdata:
            try:
                os.remove(f)
            except IOError:
                continue


class AtomsTestFixture(unittest.TestCase):
    """Mixin unittest.TestCase class defining setUp method to generate list
    of atoms."""

    def setUp(self):
        self.atoms = \
            generate_atoms(generator_class='SWNTGenerator', n=10, m=0, nz=5)
        self.atoms.assign_unique_ids()
