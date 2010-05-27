import unittest
from Products.Silva.testing import FunctionalLayer, Browser
from base64 import b64encode
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from Products.Silva.tests.helpers import publish_object


def trim_url(url):
    if url.endswith('/'):
        return url[:-1]
    return url

class BaseTest(unittest.TestCase):

    layer = FunctionalLayer
    host_base = 'http://localhost'

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('pub', 'Publication')
        self.publication = getattr(self.root, 'pub')

        factory = self.publication.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('doc', 'Document title')
        self.doc = getattr(self.publication, 'doc')

        self.intids = getUtility(IIntIds)
        self.browser = Browser()

    def _login(self, username="manager", password=""):
        self.browser.addHeader('Authorization',
            "Basic %s:%s" % (username, password))


class TestGhostAdd(BaseTest):

    def setUp(self):
        super(TestGhostAdd, self).setUp()
        self._login()

    def test_add_ghost_save(self):
        intid = self.intids.register(self.doc)
        form = self._get_add_form('Silva Ghost')
        id_field = form.getControl(name="form.field.id")
        id_field.value = 'someghost'
        reference_field = form.getControl(name="form.field.haunted")
        reference_field.value = str(intid)
        form.submit(name='form.action.save')

        self.assertEquals('200 OK', self.browser.status)
        self.assertTrue(self.root.someghost)
        self.assertEquals('http://localhost/root/edit',
            self.browser.url)

    def test_add_ghost_save_and_edit(self):
        intid = self.intids.register(self.doc)
        form = self._get_add_form('Silva Ghost')
        id_field = form.getControl(name="form.field.id")
        id_field.value = 'someghost'
        reference_field = form.getControl(name="form.field.haunted")
        reference_field.value = str(intid)
        form.submit(name='form.action.save_edit')

        self.assertEquals('200 OK', self.browser.status)
        self.assertTrue(self.root.someghost)
        self.assertEquals('http://localhost/root/someghost/edit',
            self.browser.url)

    def test_add_ghost_cancel(self):
        form = self._get_add_form('Silva Ghost')
        form.submit(name="form.action.cancel")
        self.assertEquals('http://localhost/root/edit',
            self.browser.url)

    def _get_add_form(self, meta_type, container=None):
        container = container or self.root
        base_url = self._get_url(container, pathsuffix='/edit')
        self.browser.open(base_url)
        self.assertEquals('200 OK', self.browser.status,
            "Couldn't get the SMI")

        select_box = self.browser.getControl(name="meta_type")
        self.assertTrue(select_box,
            "Couldn't get the select box for adding contents")
        select_mt_option = select_box.getControl(value=meta_type)
        self.assertTrue(select_mt_option,
            "Couldn't find the option in meta types select box")
        select_box.value = [meta_type]
        button = self.browser.getControl(name="add_object:method")
        button.click()
        self.assertEquals(trim_url("%s" % base_url),
            trim_url(self.browser.url))
        return self.browser.getForm(name="add_object")

    def _get_url(self, object, pathsuffix=""):
        opath = "/".join(object.getPhysicalPath())
        return self.host_base + opath + pathsuffix


class TestGhostViewBase(BaseTest):

    def setUp(self):
        super(TestGhostViewBase, self).setUp()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhost('docghost', None, haunted=self.doc)
        self.ghost = getattr(self.root, 'docghost')


class TestGhostViewNotPublished(TestGhostViewBase):

    def test_view_before_publish(self):
        error = None
        self.browser.open(self.host_base + '/root/docghost')
        self.assertEquals('200 OK', self.browser.status)
        self.assertTrue('is not viewable' in self.browser.contents)
        self.assertTrue('Document title' not in self.browser.contents)

    def test_preview_as_admin_before_publish(self):
        self._login()
        self.browser.open(self.host_base + '/root/++preview++/docghost')
        self.assertEquals("200 OK", self.browser.status)
        self.assertTrue('is not viewable' not in self.browser.contents)
        self.assertTrue('is broken' in self.browser.contents)


class TestGhostViewGhostPublished(TestGhostViewBase):

    def setUp(self):
        super(TestGhostViewGhostPublished, self).setUp()
        publish_object(self.ghost)

    def test_view(self):
        """ The ghost is published but not the document
        so the ghost is broken
        """
        self.browser.open(self.host_base + '/root/docghost')
        self.assertEquals("200 OK", self.browser.status)
        self.assertTrue('is not viewable' not in self.browser.contents)
        self.assertTrue('is broken' in self.browser.contents)


class TestGhostViewGhostAndDocPublished(TestGhostViewGhostPublished):

    def setUp(self):
        super(TestGhostViewGhostAndDocPublished, self).setUp()
        publish_object(self.doc)

    def test_view(self):
        self.browser.open(self.host_base + '/root/docghost')
        self.assertEquals("200 OK", self.browser.status)
        self.assertTrue('is not viewable' not in self.browser.contents)
        self.assertTrue('Document title' in self.browser.contents)

    def test_preview_as_admin_before_publish(self):
        self._login()
        self.browser.open(self.host_base + '/root/++preview++/docghost')
        self.assertEquals("200 OK", self.browser.status)
        self.assertTrue('is not viewable' not in self.browser.contents)
        self.assertTrue('Document title' in self.browser.contents)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGhostAdd))
    suite.addTest(unittest.makeSuite(TestGhostViewNotPublished))
    suite.addTest(unittest.makeSuite(TestGhostViewGhostPublished))
    suite.addTest(unittest.makeSuite(TestGhostViewGhostAndDocPublished))
    return suite


