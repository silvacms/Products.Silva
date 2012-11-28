# -*- coding: utf-8 -*-
# Copyright (c) 2003-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.component import getUtility
from zope.interface.verify import verifyObject

from Products.Silva.ftesting import public_settings
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
        factory.manage_addFolder('other', 'Other')

        factory = self.root.other.manage_addProduct['Silva']
        factory.manage_addIndexer('indexer', 'Indexer of nothing')
        self.root.other.indexer.update()

        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addAutoTOC('index', 'Index of the folder')
        factory.manage_addMockupVersionedContent('alpha', 'Alpha')
        factory.manage_addMockupVersionedContent('beta', 'Beta')
        factory.manage_addMockupVersionedContent('gamma', 'Gamma')
        factory.manage_addMockupVersionedContent('omega', 'Omega')
        factory.manage_addMockupVersionedContent('kappa', 'Kappa')
        factory.manage_addMockupVersionedContent('ultra', None) # no title
        factory.manage_addGhost('ghost', None, haunted=self.root.folder.kappa)

        # Add some anchors.
        folder = self.root.folder
        folder.alpha.set_entries([('anchor_alpha', 'Anchor Alpha'),
                                  ('anchor_empty', '')])
        folder.beta.set_entries([('anchor_alpha', 'Anchor Beta'),
                                 ('anchor_beta', 'Anchor Tetra')])
        folder.gamma.set_entries([('anchor_gamma', 'Anchor Gamma')])
        folder.kappa.set_entries([('anchor_kappa', 'Anchor Tetra')])
        folder.ultra.set_entries([('anchor_ultra', 'Anchor Ultra')])

        # Publish some documents.
        IPublicationWorkflow(folder.alpha).publish()
        IPublicationWorkflow(folder.beta).publish()
        IPublicationWorkflow(folder.kappa).publish()
        IPublicationWorkflow(folder.ghost).publish()
        IPublicationWorkflow(folder.ultra).publish()

        # now create the indexer itself
        factory.manage_addIndexer('indexer', 'Indexer of letters')
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
            folder.indexer.get_index_entry(''),
            [])
        self.assertItemsEqual(
            folder.indexer.get_index_entry('Anchor Zeta'),
            [])
        self.assertItemsEqual(
            folder.indexer.get_index_entry('Anchor Ultra'),
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

    def test_view(self):
        """Test the public view of an indexer.
        """
        with self.layer.get_browser(public_settings) as browser:
            self.assertEqual(browser.open('/root/folder/indexer'), 200)
            self.assertEqual(browser.inspect.title, ['Indexer of letters'])

            self.assertEqual(browser.open('/root/other/indexer'), 200)
            self.assertEqual(browser.inspect.title, ['Indexer of nothing'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IndexerTestCase, 'test'))
    return suite
