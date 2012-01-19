
import unittest

from zope.component import queryUtility
from zope.interface.verify import verifyObject

from silva.core.interfaces import IMimeTypeClassifier
from Products.Silva.tests import helpers
from Products.Silva.testing import FunctionalLayer


class MimetypeClassifierTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

    def create_test_file(self, filename):
        with helpers.open_test_file(filename) as file_handle:
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFile('testfile', 'Test File', file_handle)
            return self.root.testfile

    def test_imlementation(self):
        classifier = queryUtility(IMimeTypeClassifier)
        self.assertTrue(verifyObject(IMimeTypeClassifier, classifier))

    def test_guess_extension(self):
        guess_extension = queryUtility(IMimeTypeClassifier).guess_extension
        self.assertEqual(guess_extension('application/msword'), '.doc')
        self.assertEqual(guess_extension('application/zip'), '.zip')
        self.assertEqual(guess_extension('image/jpeg'), '.jpeg')

    def test_guess_type(self):
        guess_type = queryUtility(IMimeTypeClassifier).guess_type
        self.assertEqual(guess_type(id='image.jpeg'), ('image/jpeg', None))
        self.assertEqual(guess_type(id='image.bmp'), ('image/bmp', None))
        self.assertEqual(guess_type(id='page.html'), ('text/html', None))
        self.assertEqual(guess_type(id='page.htm'), ('text/html', None))
        self.assertEqual(
            guess_type(id='page.xhtml'),
            ('application/xhtml+xml', None))
        self.assertEqual(
            guess_type(id='document.doc'),
            ('application/msword', None))
        self.assertEqual(
            guess_type(id='archive.tgz'),
            ('application/x-tar', 'gzip'))
        self.assertEqual(
            guess_type(id='archive.zip'),
            ('application/zip', None))

    def test_image_png_filename(self):
        test_file = self.create_test_file('photo.tif')

        guess_filename = queryUtility(IMimeTypeClassifier).guess_filename
        self.assertEqual(guess_filename(test_file, 'image'), 'image.tiff')
        self.assertEqual(test_file.get_filename(), 'image.tiff')

    def test_image_png_filename_with_extension(self):
        test_file = self.create_test_file('photo.tif')

        guess_filename = queryUtility(IMimeTypeClassifier).guess_filename
        self.assertEqual(guess_filename(test_file, 'image.jpg'), 'image.tiff')
        self.assertEqual(test_file.get_filename(), 'image.tiff')

    def test_tar_gz_filename(self):
        test_file = self.create_test_file('images.tar.gz')

        guess_filename = queryUtility(IMimeTypeClassifier).guess_filename
        self.assertEqual(guess_filename(test_file, 'files'), 'files.gz')
        self.assertEqual(test_file.get_filename(), 'files.gz')

    def test_tar_gz_filename_with_partial_extension(self):
        test_file = self.create_test_file('images.tar.gz')

        guess_filename = queryUtility(IMimeTypeClassifier).guess_filename
        self.assertEqual(guess_filename(test_file, 'files.tar'), 'files.tar.gz')
        self.assertEqual(test_file.get_filename(), 'files.tar.gz')

    def test_tar_gz_filename_with_extension(self):
        test_file = self.create_test_file('images.tar.gz')

        guess_filename = queryUtility(IMimeTypeClassifier).guess_filename
        self.assertEqual(guess_filename(test_file, 'files.tar.gz'), 'files.tar.gz')
        self.assertEqual(test_file.get_filename(), 'files.tar.gz')

    def test_zip_filename(self):
        test_file = self.create_test_file('test1.zip')

        guess_filename = queryUtility(IMimeTypeClassifier).guess_filename
        self.assertEqual(guess_filename(test_file, 'files'), 'files.zip')
        self.assertEqual(test_file.get_filename(), 'files.zip')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MimetypeClassifierTestCase))
    return suite
