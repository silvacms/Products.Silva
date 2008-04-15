"""Test the generic export feature.
"""

__author__ ="sylvain@infrae.com"
__format__ ="plaintext"
__version__ ="$Id$"

from zope.interface import implements, classImplementsOnly
from zope.interface.verify import verifyObject
from zope.component import getGlobalSiteManager, getUtility
from zope.component.interfaces import ComponentLookupError
from zope.schema.interfaces import IVocabulary

import SilvaTestCase
from Products.Silva.adapters import interfaces
from Products.Silva.utility import interfaces as interfaces_utility
from Products.SilvaDocument import interfaces as interfaces_document

class DummyExporter(object):

    implements(interfaces.IContentExporter)

    name = 'Dummy Exporter'
    extension = 'dummy'

    def __init__(self, context):
        self.context = context

    def export(self, settings):
        pass


class ExportTestCase(SilvaTestCase.SilvaTestCase):
    """Test the genereic export feature.
    """

    def afterSetUp(self):
        """Setup some default content.
        """
        from Products.Silva.Link import manage_addLink
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva Document')
        testdocument = self.add_document(
            self.root,
            'testdocument',
            'something inside')

    def test_listExport(self):

        # You can list available exporter
        voc = self.root.export_content_format()
        self.failUnless(verifyObject(IVocabulary, voc),
                        "List exporter doesn't return a vocabulary")
        self.assertEqual([(u'zip', 'Full Media (zip)')],
                         [(v.value, v.title) for v in voc],
                         "Cannot list exporter")

        # You can list them against a ref
        ref = self.root.create_ref(self.root.testdocument)
        voc = self.root.export_content_format(ref)
        self.assertEqual([(u'zip', 'Full Media (zip)')],
                         [(v.value, v.title) for v in voc],
                         "Cannot list exporter using a ref")

        # We can register exporter for specific content
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(DummyExporter,
                            (interfaces_document.IDocument,),
                            interfaces.IContentExporter,
                            'dummy')

        # Folder will stay unchanged
        voc = self.root.export_content_format()
        self.assertEqual([(u'zip', 'Full Media (zip)')],
                         [(v.value, v.title) for v in voc],
                         "Test list specific exporter fails")

        # But the exporter is available on document
        voc = self.root.testdocument.export_content_format()
        self.assertEqual([(u'zip', 'Full Media (zip)'),
                          (u'dummy', 'Dummy Exporter')],
                         [(v.value, v.title) for v in voc],
                         "Test list specific exporter fails")


    def test_exportUtility(self):

        # There is an utility which manage export feature
        utility = getUtility(interfaces_utility.IExportUtility)()
        self.failUnless(verifyObject(interfaces_utility.IExportUtility, 
                                     utility),
                        "The export utility does not implement its interface correctly")

        # We have a function to list exporter (see test_listExport),
        # which return a vocabulary
        voc = utility.listContentExporter(self.root)
        self.assertEqual([(u'zip', 'Full Media (zip)')],
                         [(v.value, v.title) for v in voc],
                         "Cannot list exporter")

        # Add we can retrieve the default zip exporter
        zip_exporter = utility.createContentExporter(self.root, 'zip')
        self.failUnless(verifyObject(interfaces.IContentExporter,
                                     zip_exporter),
                        "Zip exporter is not a content exporter")

        # A non-existant exporter give a lookup error error
        self.assertRaises(ComponentLookupError, 
                          utility.createContentExporter, self.root, 'invalid')



import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ExportTestCase))
    return suite    
