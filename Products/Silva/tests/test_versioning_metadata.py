

import unittest

from zope.component import getUtility

from Products.Silva.testing import FunctionalLayer
from Products.SilvaMetadata.interfaces import IMetadataService, ReadOnlyError


class MetadataVersioningTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'Document')

    def test_versioned_content_metadata(self):
        """Test that you can access the metadata from the versioned
        content, but not change it.
        """
        service = getUtility(IMetadataService)

        document = self.root.document
        version = self.root.document.get_editable()

        # Now it should work, you should get the metadata of the document
        document_binding = service.getMetadata(document)
        self.assertNotEqual(document_binding, document)
        self.assertEqual(
            document_binding.get('silva-content', 'maintitle'),
            u"Document")
        self.assertEqual(
            service.getMetadataValue(document, 'silva-content', 'maintitle'),
            u"Document")

        # You can't change the value.
        with self.assertRaises(ReadOnlyError):
            document_binding.setValues('silva-content', {'maintitle': u'Ghost'})

        # Nothing changed.
        document_binding = service.getMetadata(document)
        self.assertEqual(
            document_binding.get('silva-content', 'maintitle'),
            u"Document")
        self.assertEqual(
            service.getMetadataValue(document, 'silva-content', 'maintitle'),
            u"Document")

        # Update document metadata
        version_binding = service.getMetadata(version)
        version_binding.setValues('silva-content', {'maintitle': u"Changed"})

        # You should see the values from the content point of view.
        document_binding = service.getMetadata(document)
        self.assertEqual(
            document_binding.get('silva-content', 'maintitle'),
            u"Changed")
        self.assertEqual(
            service.getMetadataValue(document, 'silva-content', 'maintitle'),
            u"Changed")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MetadataVersioningTestCase))
    return suite
