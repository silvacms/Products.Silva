# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from cStringIO import StringIO

from zope.component import queryUtility
from zope.interface.verify import verifyObject

from silva.core.interfaces import IMimeTypeClassifier
from Products.Silva.testing import FunctionalLayer


class MimetypeClassifierTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

    def create_test_file(self, filename, id=None):
        with self.layer.open_fixture(filename) as file_handle:
            factory = self.root.manage_addProduct['Silva']
            if id is None:
                id = 'testfile'
            factory.manage_addFile(id, 'Test File', file_handle)
            return self.root._getOb(id)

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
        self.assertEqual(
            guess_type(id='document.doc'),
            ('application/msword', None))
        self.assertEqual(
            guess_type(id='page.xhtml'),
            ('application/xhtml+xml', None))
        self.assertEqual(
            guess_type(id='archive.tgz'),
            ('application/x-tar', 'gzip'))
        self.assertEqual(
            guess_type(id='archive.zip'),
            ('application/zip', None))
        self.assertEqual(guess_type(id='image.jpeg'), ('image/jpeg', None))
        self.assertIn(
            guess_type(id='image.bmp'),
            set([('image/bmp', None), ('image/x-ms-bmp', None)]))
        self.assertEqual(guess_type(id='page.html'), ('text/html', None))
        self.assertEqual(guess_type(id='page.htm'), ('text/html', None))

    def test_image_tiff_filename(self):
        test_file = self.create_test_file('photo.tif')

        guess_filename = queryUtility(IMimeTypeClassifier).guess_filename
        self.assertEqual(guess_filename(test_file, 'image'), 'image.tiff')
        self.assertEqual(test_file.get_filename(), 'image.tiff')

    def test_image_tiff_filename_with_extension(self):
        test_file = self.create_test_file('photo.tif')

        guess_filename = queryUtility(IMimeTypeClassifier).guess_filename
        self.assertEqual(guess_filename(test_file, 'image.jpg'), 'image.tiff')
        self.assertEqual(test_file.get_filename(), 'image.tiff')

    def test_image_jpg_filename(self):
        test_file = self.create_test_file('torvald.jpg')
        guess_filename = queryUtility(IMimeTypeClassifier).guess_filename

        # We use by default already set filename, in lower case if
        # none specified
        test_file.set_filename('IMAGE.JPG')
        self.assertEqual(guess_filename(test_file, 'photo'), 'photo.jpg')
        self.assertEqual(test_file.get_filename(), 'photo.jpg')

        # Or the one given if it is compatible
        self.assertEqual(guess_filename(test_file, 'photo.JPEG'), 'photo.jpeg')
        self.assertEqual(test_file.get_filename(), 'photo.jpeg')

        self.assertEqual(guess_filename(test_file, 'photo.exe'), 'photo.jpeg')
        self.assertEqual(test_file.get_filename(), 'photo.jpeg')

    def test_tar_gz_filename(self):
        test_file = self.create_test_file('images.tar.gz')

        guess_filename = queryUtility(IMimeTypeClassifier).guess_filename
        self.assertEqual(guess_filename(test_file, 'files'), 'files.tar.gz')
        self.assertEqual(test_file.get_filename(), 'files.tar.gz')

    def test_tar_gz_filename_with_partial_extension(self):
        test_file = self.create_test_file('images.tar.gz')

        guess_filename = queryUtility(IMimeTypeClassifier).guess_filename
        self.assertEqual(guess_filename(test_file, 'files.tar'), 'files.tar.gz')
        self.assertEqual(test_file.get_filename(), 'files.tar.gz')

    def test_tar_gz_filename_with_extension(self):
        test_file = self.create_test_file('images.tar.gz')

        guess_filename = queryUtility(IMimeTypeClassifier).guess_filename
        self.assertEqual(
            guess_filename(test_file, 'files.tar.gz'),
            'files.tar.gz')
        self.assertEqual(test_file.get_filename(), 'files.tar.gz')

    def test_zip_filename(self):
        test_file = self.create_test_file('test1.zip')

        guess_filename = queryUtility(IMimeTypeClassifier).guess_filename
        self.assertEqual(guess_filename(test_file, 'files'), 'files.zip')
        self.assertEqual(test_file.get_filename(), 'files.zip')

    def test_id_with_ext(self):
        file = self.create_test_file('dark_energy.txt', id='test_file.txt')
        self.assertEquals(file.get_content_type(), 'text/plain; charset=utf-8')

        with self.layer.open_fixture('torvald.jpg') as image:
            file.set_file(image)
        self.assertEquals(file.get_content_type(), 'image/jpeg')

        with self.layer.open_fixture('torvald.jpg') as image:
            # we replace the file with a StringIO. StringIO doesn't have
            # a `name` attribute which makes the mimetype guess to use the id
            # of the Silva File object.
            io = StringIO(image.read())
            try:
                file.set_file(io)
            finally:
                io.close()

        self.assertEquals(file.get_content_type(), 'text/plain; charset=utf-8')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MimetypeClassifierTestCase))
    return suite
