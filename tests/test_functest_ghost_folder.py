import unittest
from Products.Silva.testing import FunctionalLayer, Browser
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from Products.Silva.tests.helpers import publish_object
from Products.Silva.tests.FunctionalTestMixin import \
    SMIFunctionalHelperMixin


class BaseTest(unittest.TestCase, SMIFunctionalHelperMixin):

    layer = FunctionalLayer
    host_base = 'http://localhost'

    def setUp(self):
        """
            Set up objects for test :

            + root (Silva root)
                |
                + folder (Silva Folder)
                    |
                    +- folderdoc (Silva Document)
                    |
                    +- pub (Silva Publication)
                        |
                        +- pubdoc (Silva Document)
        """
        self.root = self.layer.get_application()

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.folder = getattr(self.root, 'folder')

        factory = self.folder.manage_addProduct['Silva']
        factory.manage_addPublication('pub', 'Publication')
        self.publication = getattr(self.folder, 'pub')

        factory = self.folder.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('folderdoc', 'Document inside `folder`')
        self.folderdoc = getattr(self.folder, 'folderdoc')

        factory = self.publication.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('pubdoc', 'Document inside `pub`')
        self.pubdoc = getattr(self.publication, 'pubdoc')

        self.intids = getUtility(IIntIds)
        self.browser = Browser()


class TestAddGhostFolder(BaseTest):
    """ Test add form for ghost folder
    """

    def setUp(self):
        super(TestAddGhostFolder, self).setUp()
        self._login(self.browser)

    def test_add_form_save(self):
        form = self._get_add_form(
            self.browser, 'Silva Ghost Folder', self.root)
        self.assertTrue(form, 'Couldn\'t get add form for ghost folder')
        self._fill_form(form)
        button = form.getControl(name="form.action.save")
        button.click()

        self.assertTrue("200 OK", self.browser.status)
        self.assertTrue(
            getattr(self.root, "ghostfolderonpublication", False),
            "Ghost folder not created.")
        self.assertTrue(self.browser.url, "http://localhost/root/edit/")

    def test_add_form_save_and_edit(self):
        form = self._get_add_form(
            self.browser, 'Silva Ghost Folder', self.root)
        self.assertTrue(form, 'Couldn\'t get add form for ghost folder')
        self._fill_form(form)
        button = form.getControl(name="form.action.save_edit")
        button.click()

        self.assertTrue("200 OK", self.browser.status)
        self.assertTrue(
            getattr(self.root, "ghostfolderonpublication", False),
            "Ghost folder not created.")
        self.assertTrue(self.browser.url,
            "http://localhost/root/ghostfolderonpublication/edit")
        self.assertEquals(self.publication,
            self.root.ghostfolderonpublication.get_haunted(),
            "haunted object should be publication")


    def test_cancel(self):
        form = self._get_add_form(
            self.browser, 'Silva Ghost Folder', self.root)
        self.assertTrue(form, 'Couldn\'t get add form for ghost folder')
        self._fill_form(form)
        button = form.getControl(name="form.action.cancel")
        button.click()
        self.assertTrue("200 OK", self.browser.status)
        self.assertFalse(
            getattr(self.root, "ghostfolderonpublication", False),
            "Ghost folder created on Cancel action")
        self.assertTrue(self.browser.url, "http://localhost/root/edit/")


    def _fill_form(self, form):
        id_field = form.getControl(name='form.field.id')
        id_field.value = 'ghostfolderonpublication'
        reference_field = form.getControl(name='form.field.haunted')
        reference_field.value = str(self.intids.register(self.publication))


class TestEditGhostFolder(BaseTest):
    """ test ghost folder edit form
    """
    def setUp(self):
        super(TestEditGhostFolder, self).setUp()
        self._login(self.browser)
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addGhostFolder(
            'ghost_folder', "Ghost folder on root/folder",
            haunted=self.folder)
        self.ghost_folder = getattr(self.root, 'ghost_folder')
        self.ghost_folder_path = "/".join(self.ghost_folder.getPhysicalPath())

    def test_edit(self):
        self.browser.open(self.host_base + self.ghost_folder_path + '/edit')
        self.assertEquals('200 OK', self.browser.status)


