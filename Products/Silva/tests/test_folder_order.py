# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer
from silva.core.interfaces import IOrderableContainer
from silva.core.interfaces import IOrderManager
from zope.interface.verify import verifyObject


class FolderOrderTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

    def test_implementation(self):
        self.assertTrue(verifyObject(IOrderableContainer, self.root.folder))
        manager = IOrderManager(self.root.folder)
        self.assertTrue(verifyObject(IOrderManager, manager))

    def test_rename_order(self):
        assert False, 'TBD'

    def test_add_orderable(self):
        assert False, 'TBD'

    def test_remove_orderable(self):
        assert False, 'TBD'

    def test_move_orderable(self):
        assert False, 'TBD'

    def test_add_nonorderable(self):
        assert False, 'TBD'

    def test_remove_nonorderable(self):
        assert False, 'TBD'

    def test_move_nonorderable(self):
        assert False, 'TBD'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FolderOrderTestCase))
    return suite
