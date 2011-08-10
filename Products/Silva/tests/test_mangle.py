# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import unittest

# Silva
from StringIO import StringIO

# Zope 2
from Products.Silva import mangle
from silva.core.interfaces import IAsset

import SilvaTestCase

class MangleIdTest(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        self.folder = folder = self.addObject(self.silva, 'Folder', 'fold',
            title='fold', create_default=0)
        self.addObject(
            folder, 'AutoTOC', 'a_content', title='a_content')
        self.addObject(
            folder, 'File', 'an_asset', title='an_asset',
            file=StringIO("foobar"))
        self.addObject(self.folder, "PageTemplate", "pt_test", "PageTemplates")

    def test_validate(self):
        id = mangle.Id(self.folder, 'some_id')
        self.assertEquals(id.validate(), id.OK)

        id = mangle.Id(self.folder, 'a_content')
        self.assertEqual(id.validate(), id.IN_USE_CONTENT)

        id = mangle.Id(self.folder, 'an_asset')
        self.assertEqual(id.validate(), id.IN_USE_ASSET)

        id = mangle.Id(self.folder, 'a_content', allow_dup=1)
        self.assertEqual(id.validate(), id.OK)

        id = mangle.Id(self.folder, 'an_asset', allow_dup=1)
        self.assertEqual(id.validate(), id.OK)

        id = mangle.Id(self.folder, 'service_foobar')
        self.assertEqual(id.validate(), id.RESERVED_PREFIX)

        # no explicitely forbidden, but would shadow method:
        id = mangle.Id(self.folder, 'implements_asset')
        self.assertEqual(id.validate(), id.RESERVED)

        id = mangle.Id(self.folder, '&*$()')
        self.assertEqual(id.validate(), id.CONTAINS_BAD_CHARS)

        id = mangle.Id(self.folder, 'index_html')
        self.assertEqual(id.validate(), id.RESERVED)

        id = mangle.Id(self.folder, 'index.html')
        self.assertEqual(id.validate(), id.OK)

        id = mangle.Id(self.folder, 'index-html')
        self.assertEqual(id.validate(), id.OK)

        # Zope does not allow any id ending with '__' in a hard boiled manner
        # (see OFS.ObjectManager.checkValidId)
        id = mangle.Id(self.folder, 'index__', allow_dup=1)
        self.assertEqual(id.validate(), id.RESERVED_POSTFIX)

        id = mangle.Id(self.folder, 'index')
        self.assertEqual(id.validate(), id.OK)

        id = mangle.Id(self.folder, 'index', interface=IAsset)
        self.assertEqual(id.validate(), id.RESERVED)

        an_asset = self.folder.an_asset
        id = mangle.Id(self.folder, 'index', instance=an_asset)
        self.assertEqual(id.validate(), id.RESERVED)

        #test IN_USE_ZOPE, by adding a non-reserved object to self.folder
        id = mangle.Id(self.folder, 'pt_test')
        self.assertEqual(id.validate(), id.IN_USE_ZOPE)

    def test_cook_id(self):
        id = mangle.Id(self.folder, u'Gro\N{LATIN SMALL LETTER SHARP S}e Datei').cook()
        self.assert_(id.isValid())
        self.assertEquals(str(id), 'Grose_Datei')
        #self.assertEquals(str(id), 'Grosse_Datei') # this would be german replacement



class MangleTest(unittest.TestCase):

    def test_unquote(self):
        self.assertEquals(
            mangle.unquote('Hello %3D Hell %26 o %3F'),
            'Hello = Hell & o ?')

    def test_urlencode(self):
        self.assertEquals(
            mangle.urlencode('http://google.com', q='world', s=12),
            'http://google.com?q=world&s=12')
        self.assertEquals(
            mangle.urlencode('http://google.com'),
            'http://google.com')

    def test_path(self):
        test_cases = [
            ('/silva/foo', '/silva/foo/bar', 'bar'),
            ('/silva/foo', '/silva/bar', '/silva/bar'),
            ('/silva/foo', '/bar', '/bar'),
           ]
        for case in test_cases:
            base_path, item_path, expected_result = case
            base_path = base_path.split('/')
            item_path = item_path.split('/')
            expected_result = expected_result.split('/')
            actual_result = mangle.Path(base_path, item_path)
            __traceback_info__ = case
            self.assertEquals(expected_result, actual_result)

    def test_list(self):
        self.assertEquals(mangle.List([]), '')
        self.assertEquals(mangle.List(['foo']), 'foo')
        self.assertEquals(mangle.List(['foo', 'bar']), 'foo and bar')
        self.assertEquals(mangle.List(['foo', 'bar', 'baz']),
            'foo, bar and baz')

    def test_absolutize(self):
        test_cases = [
            ('/silva/a/s', 'foo/bar', '/silva/a/foo/bar'),
            ('/silva/a/s/', 'foo/bar', '/silva/a/s/foo/bar'),
            ('/silva/a/s/', './foo/bar', '/silva/a/s/foo/bar'),
            ('/silva/a/s/', '/silva/bar', '/silva/bar'),
            ('/silva/a/s/', '../../foo', '/silva/foo'),
            ('/silva/a/s/', '../../../../../foo', '../../../../../foo')
           ]
        for case in test_cases:
            base_path, item_path, expected_result = case
            base_path = base_path.split('/')
            item_path = item_path.split('/')
            expected_result = expected_result.split('/')
            actual_result = mangle.Path.toAbsolute(base_path, item_path)
            __traceback_info__ = case
            self.assertEquals(expected_result, actual_result)

    def test_strip(self):
        s = mangle.Path.strip(['', 'foo', '.', 'bar'])
        self.assertEquals(s, ['', 'foo', 'bar'])

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MangleIdTest))
    suite.addTest(unittest.makeSuite(MangleTest))
    return suite

