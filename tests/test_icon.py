# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from StringIO import StringIO

# Zope 2
from ZPublisher.HTTPRequest import FileUpload

# Silva
from silva.core import interfaces
from zope.interface.verify import verifyObject

from Products.Silva.icon import IconRegistry

import SilvaTestCase

class Request(object):
    filename = None
    headers = {}
    file = None

class RegistryTest(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        fields = Request()
        fields.filename = 'afilename.pdf'
        fields.file = StringIO("a nice pdf ;)")
        upload = FileUpload(fields)
        self.silva.manage_addProduct['Silva'].manage_addFile(
            'pdf', 'pdf file', upload)

        fields = Request()
        fields.filename = 'anoterfilename'
        fields.file = StringIO("just plain data")
        upload = FileUpload(fields)
        self.silva.manage_addProduct['Silva'].manage_addFile(
            'text', 'text file', upload)

    def test_registry(self):
        # Be sure we get the correct mimetype from the pdf file.
        self.assertEquals(
            self.silva.pdf.get_mime_type(),
            'application/pdf')

        r = IconRegistry()
        self.failUnless(verifyObject(interfaces.IIconRegistry, r))

        r.registerIcon(('meta_type', 'Silva Root'), 'root.png')
        r.registerIcon(('mime_type', 'text/plain'), 'file_text.png')
        r.registerIcon(
            ('mime_type', 'application/octet-stream'), 'file.png')
        r.registerIcon(('mime_type', 'application/pdf'), 'file_pdf.png')

        self.assertEquals(
            r.getIconByIdentifier(('meta_type', 'Silva Root')),
            'root.png')
        self.assertEquals(
            r.getIconByIdentifier(('mime_type', 'application/octet-stream')),
            'file.png')
        self.assertRaises(
            ValueError, r.getIconByIdentifier, ('meta_type', 'Foo Bar'))

        self.assertEquals(r.getIcon(self.silva), 'root.png')
        self.assertEquals(r.getIcon(self.silva.pdf), 'file_pdf.png')
        self.assertEquals(r.getIcon(self.silva.text), 'file_text.png')
        self.assertRaises(ValueError, r.getIcon, Request())

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RegistryTest))
    return suite

