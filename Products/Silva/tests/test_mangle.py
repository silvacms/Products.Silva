# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import unittest

# Zope 2
from Products.Silva import mangle
from Products.Silva.testing import FunctionalLayer
from silva.core.interfaces import IAsset


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
    suite.addTest(unittest.makeSuite(MangleIdTestCase))
    return suite

