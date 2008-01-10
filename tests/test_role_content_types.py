import re, os.path
import unittest
import test_login
import SilvaTestCase
from urllib2 import HTTPError
from Products.Five.testbrowser import Browser

# Expected state of creation
fail_login = object()
fail_nothing_addable = object()
fail_not_addable = object()
success = object()

def _openFile(filename):
    name = os.path.dirname(__file__)
    return open(name + '/' + filename)

class MixinRoleContent(test_login.MixinLoginLogout):

    def role_logout(self, browser):
        self.do_logout(browser)

    def role_login(self, browser, user_name):
        role = SilvaTestCase.users[user_name]['role']
        password = SilvaTestCase.users[user_name]['password']
        url = '%s/edit' % self.getRoot().absolute_url()
        self.do_login(browser, url, user_name, password)
        p = re.compile('logout\s+%s' % role)
        p.findall(browser.contents)
        self.failUnless(p, 'The role does not match logout message')

    def do_make_content(self, user_name, content_type, creator, result):
        browser = Browser()
        # Test role login
        try:
            browser
        except HTTPError, err:
            if result is fail_login:
                self.assertEquals(str(err), 'HTTP Error 401: Unauthorized')
            else:
                self.fail()
        self.role_login(browser, user_name)
        # Test if role has access to no content_types
        try:
            meta_type = browser.getControl(name="meta_type")
        except LookupError:
            if result is fail_nothing_addable:
                self.role_logout(browser)
                return
            self.fail()
        # Test if role has access to content_type
        if result is fail_not_addable:
            self.failIf(content_type in meta_type.options, 'Role can access meta_type')
        else:
            self.failUnless(content_type in meta_type.options, 'Content type is
                            not included as a meta_type')
            # Create the content 
            browser.getControl(name='meta_type').value = [content_type]
            browser.getControl(name='add_object:method').click()
            browser.getControl(name='field_object_id').value = 'test_content'
            # Check for special fields
            if creator:
               creator(browser)
            browser.getControl(name='add_submit').click()
            self.failUnless('Added %s' % content_type in browser.contents,
                            'Content type is not included in submit feedback
                            message')
            self.failUnless('test_content' in browser.contents)

            # Delete the content
            browser.getControl(name='ids:list').value = ['test_content']
            browser.getControl(name='tab_edit_delete:method').click()
            self.failUnless('Deleted' in browser.contents)

        self.role_logout(browser)
        self.assertEquals('You have been logged out.' in browser.contents, True)

        
class ContentTypeTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                         MixinRoleContent):
    """
       make a document as each role
       login as role
       goto select content type document
       make document
         catch failure
       delete document
       logout
    """
   
    # Silva Document
    def test_make_document(self):
        self.do_make_content(SilvaTestCase.user_manager,'Silva Document',
                              self.fill_create_title_field, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor,'Silva Document',
                              self.fill_create_title_field, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Document',
                              self.fill_create_title_field, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Document',
                              self.fill_create_title_field, success)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Document',
                              self.fill_create_title_field, fail_nothing_addable)
    
    # Silva Folder       
    def test_make_folder(self):
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                            self.fill_create_folderish_field, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Folder',
                            self.fill_create_folderish_field, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Folder',
                            self.fill_create_folderish_field, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Folder',
                            self.fill_create_folderish_field, success)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Folder',
                            self.fill_create_folderish_field, fail_nothing_addable)
    
    # Silva Publication
    def test_make_publication(self):
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                            self.fill_create_folderish_field, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Publication',
                            self.fill_create_folderish_field, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Publication',
                            self.fill_create_folderish_field, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Publication',
                            self.fill_create_folderish_field, fail_not_addable)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Publication',
                            self.fill_create_folderish_field, fail_nothing_addable)
    
    # Silva AutoTOC
    def test_make_auto_toc(self):
        self.do_make_content(SilvaTestCase.user_manager, 'Silva AutoTOC',
                            self.fill_create_depth_field, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva AutoTOC',
                            self.fill_create_depth_field, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva AutoTOC',
                            self.fill_create_depth_field, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva AutoTOC',
                            self.fill_create_depth_field, success)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva AutoTOC',
                            self.fill_create_depth_field, fail_nothing_addable)
    
    # Silva Find
    def test_make_find(self):
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Find',
                              self.fill_create_title_field, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Find',
                              self.fill_create_title_field, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Find',
                              self.fill_create_title_field, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Find',
                              self.fill_create_title_field, fail_not_addable)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Find',
                              self.fill_create_title_field, fail_nothing_addable)
    
    # Silva Ghost
    def test_make_ghost(self):
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Ghost',
                             self.fill_create_ghost_url_field, fail_nothing_addable)
    
    # Silva Ghost Folder
    def test_make_ghost(self):
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, fail_not_addable)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, fail_nothing_addable)
    
    # Silva Link Absolute
    def test_make_link(self):
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Link',
                             self.fill_create_link_fields, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Link',
                             self.fill_create_link_fields, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Link',
                             self.fill_create_link_fields, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Link',
                             self.fill_create_link_fields, success)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Link',
                             self.fill_create_link_fields, fail_nothing_addable)
    
    # Silva Link Absolute
    def test_make_indexer(self):
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Indexer',
                             self.fill_create_title_field, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Indexer',
                             self.fill_create_title_field, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Indexer',
                             self.fill_create_title_field, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Indexer',
                             self.fill_create_title_field, fail_not_addable)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Indexer',
                             self.fill_create_title_field, fail_nothing_addable)
     
    # Silva File
    def test_make_file(self):
        self.do_make_content(SilvaTestCase.user_manager, 'Silva File',
                             self.fill_create_file_field, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva File',
                             self.fill_create_file_field, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva File',
                             self.fill_create_file_field, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva File',
                             self.fill_create_file_field, success)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva File',
                             self.fill_create_file_field, fail_nothing_addable)
     
    # Silva Image
    def test_make_image(self):
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Image',
                             self.fill_create_image_fields, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Image',
                             self.fill_create_image_fields, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Image',
                             self.fill_create_image_fields, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Image',
                             self.fill_create_image_fields, success)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Image',
                             self.fill_create_image_fields, fail_nothing_addable)

    def fill_create_image_fields(self, browser):
        self.fill_create_title_field(browser)
        self.fill_create_image_field(browser)

    def fill_create_file_fields(self, browser):
        self.fill_create_title_field(browser)
        self.fill_create_file_field(browser)

    def fill_create_link_fields(self, browser):
        self.fill_create_title_field(browser)
        self.fill_create_url_field(browser)
        self.fill_create_link_type_field(browser)

    def fill_create_image_field(self, browser):
        browser.getControl(name='field_file').add_file(_openFile('torvald.jpg'), 'image/jpeg', 'torvald.jpg')

    def fill_create_file_field(self, browser):
        browser.getControl(name='field_file').add_file(_openFile('test_role_content_types.py'), 'text/plain', 'test.txt')

    def fill_create_url_field(self, browser):
        browser.getControl(name='field_url').value = 'index'

    def fill_create_link_type_field(self, browser):
        browser.getControl(name='field_link_type').value = ['absolute']
                             
    def fill_create_title_field(self, browser):
        browser.getControl(name='field_object_title').value = 'test content'

    def fill_create_folderish_field(self, browser):
        self.fill_create_title_field(browser)
        browser.getControl(name='field_policy_name').value = ['Silva Document']
    
    def fill_create_depth_field(self, browser):
        self.fill_create_title_field(browser)
        browser.getControl(name='field_depth').value = '-1'

    def fill_create_ghost_url_field(self, browser):
        browser.getControl(name='field_content_url').value = 'index'

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentTypeTestCase))
    return suite
