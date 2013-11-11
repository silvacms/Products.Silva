# -*- coding: utf-8 -*-
# Copyright (c) 2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Acquisition import aq_chain
from DateTime import DateTime

from zope.component import getUtility
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer, Transaction
from silva.core.interfaces import IGhostAsset, IImageIncluable
from silva.core.interfaces.errors import EmptyInvalidTarget
from silva.core.services.interfaces import IMetadataService


class GhostAssetTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            with self.layer.open_fixture('silva.png') as stream:
                factory.manage_addImage('logo', 'Silva Logo', stream)
            with self.layer.open_fixture('dark_energy.txt') as stream:
                factory.manage_addFile('text', 'Text file', stream)

        with Transaction():
            metadata = getUtility(IMetadataService).getMetadata(self.root.logo)
            metadata.setValues(
                'silva-extra',
                {'modificationtime': DateTime('2010-04-25T12:00:00Z')})

        self.assertEqual(
            self.root.logo.get_modification_datetime(),
            DateTime('2010-04-25T12:00:00Z'))

    def test_haunt_image(self):
        """Create and test a Ghost Asset content type that haunt an image.
        """
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addGhostAsset('ghost', None, haunted=self.root.logo)

        self.assertIn('ghost', self.root.objectIds())
        ghost = self.root._getOb('ghost')
        self.assertTrue(verifyObject(IGhostAsset, ghost))
        self.assertIn(ghost, self.root.get_non_publishables())
        self.assertEqual(ghost.get_link_status(), None)
        self.assertEqual(ghost.get_haunted(), self.root.logo)
        self.assertEqual(ghost.get_filename(), 'logo.png')
        self.assertEqual(ghost.get_mime_type(), 'image/png')
        self.assertTrue(IImageIncluable.providedBy(ghost))
        self.assertEqual(
            ghost.get_file_size(),
            self.root.logo.get_file_size())
        self.assertEqual(
            ghost.get_modification_datetime(),
            self.root.logo.get_modification_datetime())
        self.assertEqual(
            aq_chain(ghost.get_haunted()),
            aq_chain(self.root.logo))

        # Now edit an break the reference.
        ghost.set_haunted(0)
        self.assertIsInstance(ghost.get_link_status(), EmptyInvalidTarget)
        self.assertEqual(ghost.get_haunted(), None)
        self.assertEqual(ghost.get_filename(), 'ghost')
        self.assertEqual(ghost.get_file_size(), 0)
        self.assertEqual(ghost.get_mime_type(), 'application/octet-stream')
        self.assertFalse(IImageIncluable.providedBy(ghost))

    def test_haunt_file(self):
        """Create and test a Ghost Asset content type that haunt a
        file.
        """
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addGhostAsset('ghost', None, haunted=self.root.text)

        self.assertIn('ghost', self.root.objectIds())
        ghost = self.root._getOb('ghost')
        self.assertTrue(verifyObject(IGhostAsset, ghost))
        self.assertIn(ghost, self.root.get_non_publishables())
        self.assertEqual(ghost.get_link_status(), None)
        self.assertEqual(ghost.get_haunted(), self.root.text)
        self.assertEqual(ghost.get_filename(), 'text')
        self.assertEqual(ghost.get_mime_type(), 'text/plain')
        self.assertFalse(IImageIncluable.providedBy(ghost))

    def test_download(self):
        """create and download a Ghost Asset content type.
        """
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addGhostAsset('ghost', None, haunted=self.root.logo)

        with self.layer.get_browser() as browser:
            self.assertEqual(browser.open('/root/ghost'), 200)
            self.assertEqual(
                len(browser.contents),
                self.root.logo.get_file_size())
            self.assertEqual(
                int(browser.headers['Content-Length']),
                self.root.logo.get_file_size())
            self.assertEqual(
                browser.headers['Content-Type'],
                'image/png')
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=logo.png')
            self.assertEqual(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertIn(
                browser.headers['Accept-Ranges'],
                ('none', 'bytes'))

    def test_head_request(self):
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addGhostAsset('ghost', None, haunted=self.root.logo)

        with self.layer.get_browser() as browser:
            self.assertEqual(browser.open('/root/ghost', method='HEAD'), 200)
            self.assertEqual(
                len(browser.contents),
                0)
            self.assertEqual(
                int(browser.headers['Content-Length']),
                self.root.logo.get_file_size())
            self.assertEqual(
                browser.headers['Content-Type'],
                'image/png')
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=logo.png')
            self.assertIn(
                browser.headers['Accept-Ranges'],
                ('none', 'bytes'))
            self.assertEqual(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GhostAssetTestCase))
    return suite
