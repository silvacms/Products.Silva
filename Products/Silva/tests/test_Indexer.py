# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $

import unittest

from zope.component import getUtility
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer
from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces import IIndexer
from silva.core.references.interfaces import IReferenceService


class IndexerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index')
        factory.manage_addMockupVersionedContent('alpha', 'Alpha')
        factory.manage_addMockupVersionedContent('beta', 'Beta')
        factory.manage_addMockupVersionedContent('gamma', 'Gamma')
        factory.manage_addMockupVersionedContent('omega', 'Omega')
        factory.manage_addMockupVersionedContent('kappa', 'Kappa')
        factory.manage_addGhost('ghost', None, haunted=self.root.folder.kappa)

        # Add some anchors.
        folder = self.root.folder
        folder.alpha.set_entries([('anchor_alpha', 'Anchor Alpha')])
        folder.beta.set_entries([('anchor_alpha', 'Anchor Beta'),
                                 ('anchor_beta', 'Anchor Tetra')])
        folder.gamma.set_entries([('anchor_gamma', 'Anchor Gamma')])
        folder.kappa.set_entries([('anchor_kappa', 'Anchor Tetra')])

        # Publish some documents.
        IPublicationWorkflow(folder.alpha).publish()
        IPublicationWorkflow(folder.beta).publish()
        IPublicationWorkflow(folder.kappa).publish()
        IPublicationWorkflow(folder.ghost).publish()

        # now create the indexer itself
        factory.manage_addIndexer('indexer', 'Indexer')
        self.root.folder.indexer.update()

        # Helper for the test.
        service = getUtility(IReferenceService)
        def resolver(obj):
            return list(service.get_references_between(
                    self.root.folder.indexer, obj, name="indexer"))[0].__name__

        self.resolver = resolver

    def test_indexer(self):
        """Verify interface.
        """
        self.assertTrue(verifyObject(IIndexer, self.root.folder.indexer))

    def test_get_index_names(self):
        self.assertEqual(
            self.root.folder.indexer.get_index_names(),
            ['Anchor Alpha', 'Anchor Beta', 'Anchor Tetra'])

    def test_get_index_entry(self):
        folder = self.root.folder
        self.assertItemsEqual(
            folder.indexer.get_index_entry('Anchor Zeta'),
            [])
        self.assertItemsEqual(
            folder.indexer.get_index_entry('Anchor Alpha'),
            [(u'Alpha', self.resolver(folder.alpha), 'anchor_alpha')])
        self.assertItemsEqual(
            folder.indexer.get_index_entry('Anchor Beta'),
            [(u'Beta', self.resolver(folder.beta), 'anchor_alpha')])
        self.assertItemsEqual(
            folder.indexer.get_index_entry('Anchor Tetra'),
            [(u'Beta', self.resolver(folder.beta), 'anchor_beta'),
             (u'Kappa', self.resolver(folder.kappa), 'anchor_kappa'),
             (u'Kappa', self.resolver(folder.ghost), 'anchor_kappa')])

    def test_remove_entry_when_remove_object(self):
        """Verify that a corresponding entry is removed when the
        object is removed.
        """
        folder = self.root.folder

        self.assertItemsEqual(
            folder.indexer.get_index_entry('Anchor Alpha'),
            [(u'Alpha', self.resolver(folder.alpha), u'anchor_alpha')])

        folder.manage_delObjects(['alpha'])

        self.assertItemsEqual(
            folder.indexer.get_index_entry('Anchor Alpha'),
            [])

    def test_remove_everything(self):
        """Verify that can remove everything without errors.
        """
        self.root.manage_delObjects(['folder'])
        self.assertFalse('folder' in self.root.objectIds())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IndexerTestCase, 'test'))
    return suite
