# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer


class AddablesTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')

    def test_set_and_get_addables(self):
        """Test that if you set addables you get what you set.
        """
        addables = ['Silva Image']
        self.root.publication.set_silva_addables_allowed_in_container(addables)
        self.assertEquals(
            self.root.publication.get_silva_addables_allowed_in_container(),
            ['Silva Image'])

    def test_root_not_addables(self):
        """Silva Root should not be addable.
        """
        self.failIf(
            'Silva Root' in self.root.get_silva_addables_all())
        self.failIf(
            'Silva Root' in
            self.root.get_silva_addables_allowed_in_container())
        self.failIf(
            'Silva Root' in
            self.root.publication.get_silva_addables_allowed_in_container())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AddablesTestCase))
    return suite
