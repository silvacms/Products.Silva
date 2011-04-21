# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from silva.core.interfaces import IContentExporter, IPublication
from silva.core.interfaces import IContentExporterRegistry
from zope.interface import implements
from zope.interface.verify import verifyObject
from zope.component import getGlobalSiteManager, getUtility
from zope.component.interfaces import ComponentLookupError
from zope.schema.interfaces import IVocabulary

from Products.Silva.testing import FunctionalLayer


class DummyExporter(object):
    implements(IContentExporter)

    name = 'Dummy Exporter'
    extension = 'dummy'

    def __init__(self, context):
        self.context = context

    def export(self, settings):
        pass


class ExporterTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

    def test_implementation(self):
        utility = getUtility(IContentExporterRegistry)
        self.assertTrue(verifyObject(IContentExporterRegistry, utility))

    def test_list(self):
        # You can list available exporter
        utility = getUtility(IContentExporterRegistry)
        available = utility.list(self.root)
        self.assertTrue(verifyObject(IVocabulary, available))
        self.assertEqual(
            [(v.value, v.title) for v in available],
            [(u'zip', 'Full Media (zip)')])

        # We can register exporter for specific content
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(
            DummyExporter, (IPublication,), IContentExporter, 'dummy')

        available = utility.list(self.root)
        self.assertEqual(
            [(v.value, v.title) for v in available],
            [(u'zip', 'Full Media (zip)'),
             (u'dummy', 'Dummy Exporter')])

        available = utility.list(self.root.folder)
        self.assertEqual(
            [(v.value, v.title) for v in available],
            [(u'zip', 'Full Media (zip)')])

        # Remove our test exporter
        gsm.unregisterAdapter(
            DummyExporter, (IPublication,), IContentExporter, 'dummy')

    def test_create(self):
        utility = getUtility(IContentExporterRegistry)
        # Add we can retrieve the default zip exporter
        exporter = utility.get(self.root, 'zip')
        self.assertTrue(verifyObject(IContentExporter, exporter))

        # A non-existant exporter give a lookup error error
        with self.assertRaises(ComponentLookupError):
            expoter = utility.get(self.root, 'invalid')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ExporterTestCase))
    return suite
