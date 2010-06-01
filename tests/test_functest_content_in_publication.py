import unittest

from SilvaTestCase import SilvaFunctionalTestCase
from SilvaBrowser import SilvaBrowser
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

class ContentTypeInPublicationTestCase(SilvaFunctionalTestCase):
    """ each role make each content type in a publication
    """

    def create_content_and_logout(self, sb, content_type, username,
                                  **fields):
        """ make content type, logout
        """
        sb.login(username, url='http://nohost/root/edit')
        self.failUnless('logout' in sb.browser.contents,
                        "logout not found on browser page. Test failed login")
        sb.make_content(content_type, **fields)
        self.failUnless(fields['id'] in sb.get_content_ids())
        sb.logout()
        return fields['id']

    def create_content_delete_logout(self, sb, content_type, username,
                                     existing_content, **fields):
        """ click into a container, make content type, delete content type,
            logout
        """
        sb.login(username, url='http://nohost/root/edit')
        self.failUnless('logout' in sb.browser.contents,
                        "logout not found on browser page. Test failed login")
        sb.click_href_labeled(existing_content)
        sb.make_content(content_type, **fields)
        self.failUnless(fields['id'] in sb.get_content_ids())
        status, url = sb.select_delete_content(fields['id'])
        self.failIf(fields['id'] in sb.get_content_ids())
        sb.logout()

    def login_delete_logout(self, sb, username, existing_content):
        """ login, select existing content, delete, logout
        """
        sb.login(username, url='http://nohost/root/edit')
        sb.select_delete_content(existing_content)
        self.failIf(existing_content in sb.get_content_ids())
        sb.logout()

    def test_silva_document_in_publication(self):
        sb = SilvaBrowser()
        existing_content = self.create_content_and_logout(
            sb, 'Silva Publication', 'manager',
            id='test_publication1', title='Test publication 1',
            policy='Silva Document')
        for username in ['manager', 'chiefeditor', 'editor', 'author']:
            self.create_content_delete_logout(sb, 'Silva Document', username,
                                              existing_content,
                                              id='test_document',
                                              title='Test document')
        self.login_delete_logout(sb, 'manager', existing_content)

    def test_silva_folder_in_publication(self):
        sb = SilvaBrowser()
        existing_content = self.create_content_and_logout(
            sb, 'Silva Publication', 'manager',
            id='test_publication1', title='Test publication 1',
            policy='Silva Document')
        for username in ['manager', 'chiefeditor', 'editor', 'author']:
            self.create_content_delete_logout(sb, 'Silva Folder', username,
                                              existing_content,
                                              id='test_folder',
                                              title='Test folder',
                                              policy='Silva Document')
        self.login_delete_logout(sb, 'manager', existing_content)

    def test_silva_publication_in_publication(self):
        sb = SilvaBrowser()
        existing_content = self.create_content_and_logout(
            sb, 'Silva Publication', 'manager',
            id='test_publication1', title='Test publication 1',
            policy='Silva Document')
        for username in ['manager', 'chiefeditor', 'editor']:
            self.create_content_delete_logout(sb, 'Silva Publication', username,
                                              existing_content,
                                              id='test_publication',
                                              title='Test publication',
                                              policy='Silva Document')
        self.login_delete_logout(sb, 'manager', existing_content)

    def test_silva_image_in_publication(self):
        sb = SilvaBrowser()
        existing_content = self.create_content_and_logout(
            sb, 'Silva Publication', 'manager',
            id='test_publication1', title='Test publication 1',
            policy='Silva Document')
        for username in ['manager', 'chiefeditor', 'editor', 'author']:
            self.create_content_delete_logout(sb, 'Silva Image', username,
                                              existing_content,
                                              id='test_image',
                                              title='Test image',
                                              image='torvald.jpg')
        self.login_delete_logout(sb, 'manager', existing_content)

    def test_silva_file_in_publication(self):
        sb = SilvaBrowser()
        existing_content = self.create_content_and_logout(
            sb, 'Silva Publication', 'manager',
            id='test_publication1', title='Test publication 1',
            policy='Silva Document')
        for username in ['manager', 'chiefeditor', 'editor', 'author']:
            self.create_content_delete_logout(sb, 'Silva File', username,
                                              existing_content,
                                              id='test_file',
                                              title='Test file',
                                              file='test.txt')
        self.login_delete_logout(sb, 'manager', existing_content)

    def test_silva_find_in_publication(self):
        sb = SilvaBrowser()
        existing_content = self.create_content_and_logout(
            sb, 'Silva Publication', 'manager',
            id='test_publication1', title='Test publication 1',
            policy='Silva Document')
        for username in ['manager', 'chiefeditor', 'editor']:
            self.create_content_delete_logout(sb, 'Silva Find', username,
                                              existing_content,
                                              id='test_find',
                                              title='Test find')
        self.login_delete_logout(sb, 'manager', existing_content)

    def test_silva_ghost_in_publication(self):
        sb = SilvaBrowser()
        intid = getUtility(IIntIds)
        refid = str(intid.register(self.root.index))
        existing_content = self.create_content_and_logout(
            sb, 'Silva Publication', 'manager',
            id='test_publication1', title='Test publication 1',
            policy='Silva Document')
        for username in ['manager', 'chiefeditor', 'editor', 'author']:
            self.create_content_delete_logout(sb, 'Silva Ghost', username,
                                              existing_content,
                                              id='test_ghost',
                                              reference=refid)
        self.login_delete_logout(sb, 'manager', existing_content)

    def test_silva_indexer_in_publication(self):
        sb = SilvaBrowser()
        existing_content = self.create_content_and_logout(
            sb, 'Silva Publication', 'manager',
            id='test_publication1', title='Test publication 1',
            policy='Silva Document')
        for username in ['manager', 'chiefeditor', 'editor']:
            self.create_content_delete_logout(sb, 'Silva Indexer', username,
                                              existing_content,
                                              id='test_indexer',
                                              title='Test indexer')
        self.login_delete_logout(sb, 'manager', existing_content)

    def test_silva_link_in_publication(self):
        # toggle absolute
        sb = SilvaBrowser()
        existing_content = self.create_content_and_logout(
            sb, 'Silva Publication', 'manager',
            id='test_publication1', title='Test publication 1',
            policy='Silva Document')
        for username in ['manager', 'chiefeditor', 'editor', 'author']:
            self.create_content_delete_logout(sb, 'Silva Link', username,
                                              existing_content,
                                              id='test_link',
                                              title='Test link',
                                              url='http://www.infrae.com')
        self.login_delete_logout(sb, 'manager', existing_content)

    def test_silva_autotoc_in_publication(self):
        sb = SilvaBrowser()
        existing_content = self.create_content_and_logout(
            sb, 'Silva Publication', 'manager',
            id='test_publication1', title='Test publication 1',
            policy='Silva Document')
        for username in ['manager', 'chiefeditor', 'editor', 'author']:
            self.create_content_delete_logout(sb, 'Silva AutoTOC', username,
                                              existing_content,
                                              id='test_autotoc',
                                              title='Test AutoTOC',
                                              depth='-1')
        self.login_delete_logout(sb, 'manager', existing_content)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentTypeInPublicationTestCase))
    return suite
