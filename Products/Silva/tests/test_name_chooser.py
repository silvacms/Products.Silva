# -*- coding: utf-8 -*-
# Copyright (c) 2013 Infrae. All rights reserved.
# -*- coding: utf-8 -*-

import unittest

from Products.Silva.testing import FunctionalLayer
from Products.Silva import mangle

from silva.core.interfaces import IAsset, ISilvaNameChooser, ContentError
from zope.interface.verify import verifyObject


class NameChooserTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_create_invalid_characters(self):
        """Invalid characters a replaced.
        """
        factory = self.root.manage_addProduct['Silva']
        with self.assertRaises(ValueError):
            factory.manage_addMockupVersionedContent('it*em', 'Item')

    def test_create_already_exists(self):
        """A content with the same name is present in the folder.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('item', 'Item')

        with self.assertRaises(ValueError):
            factory.manage_addMockupVersionedContent('item', 'Item')

    def test_create_unicode(self):
        """You can create a content with an unicode id.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent(u'item', u'Title')
        item = self.root._getOb('item', None)
        self.assertIsNotNone(item)

    def test_create_unicode_invalid_characters(self):
        """You cannot create a content with an invalid id.
        """
        factory = self.root.manage_addProduct['Silva']
        with self.assertRaises(ValueError):
            factory.manage_addMockupVersionedContent(u'itéám', u'Title')

    def test_silva_name_chooser(self):
        """Test name chooser implementation for Silva contents.

        checkName should raise ContentErrror for invalid ids, return
        True for valid ones.
        """
        chooser = ISilvaNameChooser(self.root)
        self.assertTrue(verifyObject(ISilvaNameChooser, chooser))

        # checkName
        self.assertTrue(chooser.checkName('valid_id', None))
        with self.assertRaises(ContentError):
            chooser.checkName('service_check', None)
        with self.assertRaises(ContentError):
            chooser.checkName('override.html', None)
        with self.assertRaises(ContentError):
            chooser.checkName('aq_parent', None)
        with self.assertRaises(ContentError):
            chooser.checkName('document__', None)
        with self.assertRaises(ContentError):
            chooser.checkName('__document', None)

    def test_zope_name_chooser(self):
        """Test name chooser implementation for Zope contents. This is
        used when adding a Silva root.

        checkName should ContentError for invalids ids, return True
        for valid ones.
        """
        factory = self.root.manage_addProduct['OFS']
        factory.manage_addFolder('folder', 'Folder')

        chooser = ISilvaNameChooser(self.root.folder)
        self.assertTrue(verifyObject(ISilvaNameChooser, chooser))

        # checkName. services are valid inside a Zope folder
        self.assertTrue(chooser.checkName('valid_id', None))
        self.assertTrue(chooser.checkName('service_check', None))
        self.assertTrue(chooser.checkName('override.html', None))
        with self.assertRaises(ContentError):
            chooser.checkName('aq_parent', None)
        with self.assertRaises(ContentError):
            chooser.checkName('document__', None)
        with self.assertRaises(ContentError):
            chooser.checkName('__document', None)


class MangleIdTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'folder')

        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addAutoTOC('info', 'Content')
        factory.manage_addFile('data', 'Asset')

        factory = self.root.folder.manage_addProduct['PageTemplates']
        factory.manage_addPageTemplate('pt_test')

    def test_validate(self):
        id = mangle.Id(self.root.folder, 'some_id')
        self.assertEquals(id.validate(), id.OK)

        id = mangle.Id(self.root.folder, 'info')
        self.assertEqual(id.validate(), id.IN_USE_CONTENT)

        id = mangle.Id(self.root.folder, 'data')
        self.assertEqual(id.validate(), id.IN_USE_ASSET)

        id = mangle.Id(self.root.folder, 'info', allow_dup=1)
        self.assertEqual(id.validate(), id.OK)

        id = mangle.Id(self.root.folder, 'data', allow_dup=1)
        self.assertEqual(id.validate(), id.OK)

        id = mangle.Id(self.root.folder, 'keys')
        self.assertEqual(id.validate(), id.RESERVED)

        id = mangle.Id(self.root.folder, 'values')
        self.assertEqual(id.validate(), id.RESERVED)

        id = mangle.Id(self.root.folder, 'service_foobar')
        self.assertEqual(id.validate(), id.RESERVED_PREFIX)

        # no explicitely forbidden, but would shadow method:
        id = mangle.Id(self.root.folder, 'content')
        self.assertEqual(id.validate(), id.RESERVED)

        id = mangle.Id(self.root.folder, '&*$()')
        self.assertEqual(id.validate(), id.CONTAINS_BAD_CHARS)

        id = mangle.Id(self.root.folder, 'index_html')
        self.assertEqual(id.validate(), id.RESERVED)

        id = mangle.Id(self.root.folder, 'index.html')
        self.assertEqual(id.validate(), id.OK)

        id = mangle.Id(self.root.folder, 'index-html')
        self.assertEqual(id.validate(), id.OK)

        # Zope does not allow any id ending with '__' in a hard boiled manner
        # (see OFS.ObjectManager.checkValidId)
        id = mangle.Id(self.root.folder, 'index__', allow_dup=1)
        self.assertEqual(id.validate(), id.RESERVED_POSTFIX)

        id = mangle.Id(self.root.folder, 'index')
        self.assertEqual(id.validate(), id.OK)

        id = mangle.Id(self.root.folder, 'index', interface=IAsset)
        self.assertEqual(id.validate(), id.RESERVED)

        data = self.root.folder.data
        id = mangle.Id(self.root.folder, 'index', instance=data)
        self.assertEqual(id.validate(), id.RESERVED)

        #test IN_USE_ZOPE, by adding a non-reserved object to self.root.folder
        id = mangle.Id(self.root.folder, 'pt_test')
        self.assertEqual(id.validate(), id.IN_USE_ZOPE)

    def test_cook_id(self):
        id = mangle.Id(
            self.root.folder,
            u'Gro\N{LATIN SMALL LETTER SHARP S}e Datei').cook()
        self.assertTrue(id.isValid())
        self.assertEqual(str(id), 'Grose_Datei')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NameChooserTestCase))
    suite.addTest(unittest.makeSuite(MangleIdTestCase))
    return suite
