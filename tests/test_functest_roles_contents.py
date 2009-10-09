import unittest
from SilvaBrowser import SilvaBrowser
from SilvaTestCase import SilvaFunctionalTestCase

class ContentTypeTestCase(SilvaFunctionalTestCase):
    """ each role make each content type
    """

    def create_content_and_delete(self, sb, content_type, username,
                                  **fields):
        """ make content type, delete content type, logout
        """
        sb.login(username, url='http://nohost/root/edit')
        self.failUnless('logout' in sb.browser.contents,
                        "logout not found on browser page. Test failed login")
        sb.make_content(content_type, **fields)
        self.failUnless(fields['id'] in sb.get_content_ids())
        status, url = sb.select_delete_content(fields['id'])
        self.failIf(fields['id'] in sb.get_content_ids())
        sb.logout()

    def test_silva_document(self):
        sb = SilvaBrowser()
        for username in ['manager', 'chiefeditor', 'editor', 'author']:
            self.create_content_and_delete(sb, 'Silva Document', username,
                                           id='test_document',
                                           title='Test document')

    def test_silva_folder(self):
        sb = SilvaBrowser()
        for username in ['manager','chiefeditor', 'editor', 'author']:
            self.create_content_and_delete(sb, 'Silva Folder', username,
                                           id='test_folder',
                                           title='Test folder',
                                           policy='Silva Document')
    def test_silva_publication(self):
        sb = SilvaBrowser()
        for username in ['manager','chiefeditor', 'editor']:
            self.create_content_and_delete(sb, 'Silva Publication', username,
                                           id='test_publication',
                                           title='Test publication',
                                           policy='Silva Document')

    def test_silva_image(self):
        sb = SilvaBrowser()
        for username in ['manager','chiefeditor', 'editor', 'author']:
            self.create_content_and_delete(sb, 'Silva Image', username,
                                           id='test_image',
                                           title='Test image',
                                           image='torvald.jpg')

    def test_silva_file(self):
        sb = SilvaBrowser()
        for username in ['manager','chiefeditor', 'editor', 'author']:
            self.create_content_and_delete(sb, 'Silva File', username,
                                           id='test_file',
                                           title='Test file',
                                           file='test.txt')

    def test_silva_find(self):
        sb = SilvaBrowser()
        for username in ['manager','chiefeditor', 'editor']:
            self.create_content_and_delete(sb, 'Silva Find', username,
                                           id='test_find',
                                           title='Test find')

    def test_silva_ghost(self):
        sb = SilvaBrowser()
        for username in ['manager','chiefeditor', 'editor', 'author']:
            self.create_content_and_delete(sb, 'Silva Ghost', username,
                                           id='test_ghost',
                                           reference='index')
    def test_silva_indexer(self):
        sb = SilvaBrowser()
        for username in ['manager','chiefeditor', 'editor']:
            self.create_content_and_delete(sb, 'Silva Indexer', username,
                                           id='test_indexer',
                                           title='Test indexer')
    def test_silva_link(self):
        sb = SilvaBrowser()
        for username in ['manager','chiefeditor', 'editor', 'author']:
            self.create_content_and_delete(sb, 'Silva Link', username,
                                           id='test_link',
                                           title='Test link',
                                           url='www.infrae.com')

    def test_silva_autotoc(self):
        sb = SilvaBrowser()
        for username in ['manager','chiefeditor', 'editor', 'author']:
            self.create_content_and_delete(sb, 'Silva AutoTOC', username,
                                           id='test_autotoc',
                                           title='Test AutoTOC',
                                           depth='-1')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentTypeTestCase))
    return suite
