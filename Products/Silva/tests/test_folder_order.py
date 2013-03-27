# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.testing import FunctionalLayer
from Products.Silva.testing import assertNotTriggersEvents

from silva.core.interfaces import IContainerManager
from silva.core.interfaces import IOrderableContainer
from silva.core.interfaces import IOrderManager
from zope.interface.verify import verifyObject


class OrderManagerTestCase(unittest.TestCase):
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

        # If you ask the position of an invalid content, or a contnet
        # that is not in the folder, you get -1
        self.assertEqual(manager.get_position(None), -1)
        self.assertEqual(manager.get_position(self.root), -1)
        self.assertEqual(len(manager), 0)

    def test_add_orderable(self):
        """We add an orderable in the folder. It is added to the order
        manager.
        """
        manager = IOrderManager(self.root.folder)
        factory = self.root.folder.manage_addProduct['Silva']

        # First item have position 0
        with assertNotTriggersEvents('ContentOrderChangedEvent'):
            factory.manage_addMockupVersionedContent('item1', 'Item 1')
        item1 = self.root.folder._getOb('item1')
        self.assertEqual(manager.get_position(item1), 0)
        self.assertEqual(len(manager), 1)

        # Next item have position 1
        with assertNotTriggersEvents('ContentOrderChangedEvent'):
            factory.manage_addMockupVersionedContent('item2', 'Item 2')
        item2 = self.root.folder._getOb('item2')
        self.assertEqual(manager.get_position(item2), 1)
        self.assertEqual(len(manager), 2)

        # The order is valid, repair return False.
        self.assertEqual(manager.repair(self.root.folder.objectValues()), False)

    def test_add_nonorderable(self):
        """We add non-orderable content in the folder. It is not added
        to the order manager.
        """
        manager = IOrderManager(self.root.folder)
        factory = self.root.folder.manage_addProduct['Silva']

        with assertNotTriggersEvents('ContentOrderChangedEvent'):
            factory.manage_addMockupAsset('asset1', 'Asset 1')
        asset1 = self.root.folder._getOb('asset1')
        self.assertEqual(manager.get_position(asset1), -1)
        self.assertEqual(len(manager), 0)

        # If you add an item if will be correctly added.
        with assertNotTriggersEvents('ContentOrderChangedEvent'):
            factory.manage_addMockupVersionedContent('item1', 'Item 1')
        item1 = self.root.folder._getOb('item1')
        self.assertEqual(manager.get_position(item1), 0)
        self.assertEqual(len(manager), 1)

        # Asset still don't go through.
        with assertNotTriggersEvents('ContentOrderChangedEvent'):
            factory.manage_addMockupAsset('asset2', 'Asset 2')
        asset2 = self.root.folder._getOb('asset2')
        self.assertEqual(manager.get_position(asset2), -1)
        self.assertEqual(len(manager), 1)


class OrderManagerModificationTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('source', 'Folder source')
        factory.manage_addFolder('target', 'Folder target')

        factory = self.root.source.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('item1', 'Item source 1')
        factory.manage_addMockupVersionedContent('item2', 'Item source 2')
        factory.manage_addMockupVersionedContent('item3', 'Item source 3')
        factory.manage_addMockupAsset('asset1', 'Asset source 1')

        factory = self.root.target.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('base1', 'Item target 1')

    def test_repair_broken_order(self):
        """We repair a broken order.
        """
        source = self.root.source
        manager = IOrderManager(source)
        # We add invalid ids to the order
        manager.order.insert(1, 'foo')
        manager.order.insert(3, 'bar')
        manager.order.insert(4, manager.order[0])

        # Order is now messed up
        self.assertEqual(manager.get_position(source.item1), 0)
        self.assertEqual(manager.get_position(source.item2), 2)
        self.assertEqual(manager.get_position(source.item3), 5)
        self.assertEqual(manager.get_position(source.asset1), -1)
        self.assertEqual(len(manager), 6)

        # repair return True.
        self.assertEqual(manager.repair(source.objectValues()), True)

        # Invalid ids have been removed
        self.assertEqual(manager.get_position(source.item1), 0)
        self.assertEqual(manager.get_position(source.item2), 1)
        self.assertEqual(manager.get_position(source.item3), 2)
        self.assertEqual(manager.get_position(source.asset1), -1)
        self.assertEqual(len(manager), 3)

    def test_reorder_orderable(self):
        """You can change the position of an orderable content.
        """
        source = self.root.source
        manager = IOrderManager(source)
        self.assertEqual(manager.get_position(source.item1), 0)
        self.assertEqual(manager.get_position(source.item2), 1)
        self.assertEqual(manager.get_position(source.item3), 2)
        self.assertEqual(manager.get_position(source.asset1), -1)
        self.assertEqual(len(manager), 3)

        self.assertEqual(manager.move(source.item1, 2), True)

        self.assertEqual(manager.get_position(source.item1), 2)
        self.assertEqual(manager.get_position(source.item2), 0)
        self.assertEqual(manager.get_position(source.item3), 1)
        self.assertEqual(manager.get_position(source.asset1), -1)
        self.assertEqual(len(manager), 3)

        self.assertEqual(manager.move(source.item2, 1), True)

        self.assertEqual(manager.get_position(source.item1), 2)
        self.assertEqual(manager.get_position(source.item2), 1)
        self.assertEqual(manager.get_position(source.item3), 0)
        self.assertEqual(manager.get_position(source.asset1), -1)
        self.assertEqual(len(manager), 3)

        # You can't move something out of the scope of movable things.
        self.assertEqual(manager.move(source.item3, -42), False)
        self.assertEqual(manager.move(source.item3, 42), False)
        # Or that doesn't belong here
        self.assertEqual(manager.move(source, 2), False)

        self.assertEqual(manager.get_position(source.item1), 2)
        self.assertEqual(manager.get_position(source.item2), 1)
        self.assertEqual(manager.get_position(source.item3), 0)
        self.assertEqual(manager.get_position(source.asset1), -1)
        self.assertEqual(len(manager), 3)

        # The order is valid, repair return False.
        self.assertEqual(manager.repair(source.objectValues()), False)

    def test_rename_orderable(self):
        """If you rename a content, its order must be keept (and not
        changed).
        """
        source = self.root.source
        manager = IOrderManager(source)
        self.assertEqual(manager.get_position(source.item1), 0)
        self.assertEqual(manager.get_position(source.item2), 1)
        self.assertEqual(manager.get_position(source.item3), 2)
        self.assertEqual(manager.get_position(source.asset1), -1)
        self.assertEqual(len(manager), 3)

        with assertNotTriggersEvents('ContentOrderChangedEvent'):
            with IContainerManager(source).renamer() as renamer:
                renamer((source.item2, 'super2', None))

        self.assertEqual(manager.get_position(source.item1), 0)
        self.assertEqual(manager.get_position(source.super2), 1)
        self.assertEqual(manager.get_position(source.item3), 2)
        self.assertEqual(manager.get_position(source.asset1), -1)
        self.assertEqual(len(manager), 3)

        # The order is valid, repair return False.
        self.assertEqual(manager.repair(source.objectValues()), False)

    def test_remove_orderable(self):
        """If we remove an orderable, it is no longer available in the
        order manager, and position of content following this one are
        changed as well.
        """
        source = self.root.source
        manager = IOrderManager(source)
        self.assertEqual(manager.get_position(source.item1), 0)
        self.assertEqual(manager.get_position(source.item2), 1)
        self.assertEqual(manager.get_position(source.item3), 2)
        self.assertEqual(manager.get_position(source.asset1), -1)
        self.assertEqual(len(manager), 3)

        item2 = source.item2
        with assertNotTriggersEvents('ContentOrderChangedEvent'):
            with IContainerManager(source).deleter() as deleter:
                self.assertEqual(deleter(item2), item2)

        self.assertEqual(manager.get_position(source.item1), 0)
        self.assertEqual(manager.get_position(source.item3), 1)
        self.assertEqual(manager.get_position(item2), -1)
        self.assertEqual(len(manager), 2)

        # The order is valid, repair return False.
        self.assertEqual(manager.repair(source.objectValues()), False)

    def test_move_orderable(self):
        """If you move an orderable, it is removed from the source
        order manager and added to the target order manager.
        """
        source = self.root.source
        target = self.root.target
        manager_source = IOrderManager(source)
        manager_target = IOrderManager(target)
        self.assertEqual(manager_source.get_position(source.item1), 0)
        self.assertEqual(manager_source.get_position(source.item2), 1)
        self.assertEqual(manager_source.get_position(source.item3), 2)
        self.assertEqual(manager_source.get_position(source.asset1), -1)
        self.assertEqual(len(manager_source), 3)
        self.assertEqual(len(manager_target), 1)

        with assertNotTriggersEvents('ContentOrderChangedEvent'):
            with IContainerManager(target).mover() as mover:
                mover(source.item2)

        item2 = source._getOb('item2', None)
        self.assertEqual(item2, None)
        item2 = target._getOb('item2', None)
        self.assertNotEqual(item2, None)

        self.assertEqual(manager_source.get_position(source.item1), 0)
        self.assertEqual(manager_source.get_position(source.item3), 1)
        self.assertEqual(len(manager_source), 2)
        self.assertEqual(manager_target.get_position(target.base1), 0)
        self.assertEqual(manager_target.get_position(target.item2), 1)
        self.assertEqual(len(manager_target), 2)

        # The order is valid, repair return False.
        self.assertEqual(manager_source.repair(source.objectValues()), False)
        self.assertEqual(manager_target.repair(target.objectValues()), False)

    def test_copy_orderable(self):
        """If we copy a orderable content, the copy is added to the
        order manager, and the other order are not touched.
        """
        source = self.root.source
        manager = IOrderManager(source)
        self.assertEqual(manager.get_position(source.item1), 0)
        self.assertEqual(manager.get_position(source.item2), 1)
        self.assertEqual(manager.get_position(source.item3), 2)
        self.assertEqual(manager.get_position(source.asset1), -1)
        self.assertEqual(len(manager), 3)

        item2 = source.item2
        with assertNotTriggersEvents('ContentOrderChangedEvent'):
            with IContainerManager(source).copier() as copier:
                copier(item2)

        self.assertEqual(manager.get_position(source.item1), 0)
        self.assertEqual(manager.get_position(source.item2), 1)
        self.assertEqual(manager.get_position(source.item3), 2)
        self.assertEqual(manager.get_position(source.copy_of_item2), 3)
        self.assertEqual(len(manager), 4)

        # The order is valid, repair return False.
        self.assertEqual(manager.repair(source.objectValues()), False)

    def test_remove_nonorderable(self):
        """If we remove an nonorderable content nothing is changed.
        """
        source = self.root.source
        manager = IOrderManager(source)
        self.assertEqual(manager.get_position(source.item1), 0)
        self.assertEqual(manager.get_position(source.item2), 1)
        self.assertEqual(manager.get_position(source.item3), 2)
        self.assertEqual(manager.get_position(source.asset1), -1)
        self.assertEqual(len(manager), 3)

        with assertNotTriggersEvents('ContentOrderChangedEvent'):
            with IContainerManager(source).deleter() as deleter:
                self.assertEqual(deleter(source.asset1), source.asset1)

        self.assertEqual(manager.get_position(source.item1), 0)
        self.assertEqual(manager.get_position(source.item2), 1)
        self.assertEqual(manager.get_position(source.item3), 2)
        self.assertEqual(len(manager), 3)

        asset1 = source._getOb('asset1', None)
        self.assertEqual(asset1, None)

    def test_move_nonorderable(self):
        """If we move an nonorderable content, nothing is changed.
        """
        source = self.root.source
        target = self.root.target
        manager_source = IOrderManager(source)
        manager_target = IOrderManager(target)
        self.assertEqual(manager_source.get_position(source.item1), 0)
        self.assertEqual(manager_source.get_position(source.item2), 1)
        self.assertEqual(manager_source.get_position(source.item3), 2)
        self.assertEqual(manager_source.get_position(source.asset1), -1)
        self.assertEqual(len(manager_source), 3)
        self.assertEqual(len(manager_target), 1)

        with assertNotTriggersEvents('ContentOrderChangedEvent'):
            with IContainerManager(target).mover() as mover:
                mover(source.asset1)

        asset1 = source._getOb('asset1', None)
        self.assertEqual(asset1, None)
        asset1 = target._getOb('asset1', None)
        self.assertNotEqual(asset1, None)

        self.assertEqual(manager_source.get_position(source.item1), 0)
        self.assertEqual(manager_source.get_position(source.item2), 1)
        self.assertEqual(manager_source.get_position(source.item3), 2)
        self.assertEqual(len(manager_source), 3)
        self.assertEqual(len(manager_target), 1)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(OrderManagerTestCase))
    suite.addTest(unittest.makeSuite(OrderManagerModificationTestCase))
    return suite
