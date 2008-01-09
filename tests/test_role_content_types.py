import re
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

class MixinRole(test_login.MixinLoginLogout):

    def role_logout(self, browser):
        self.do_logout(browser)

    def role_login(self, browser, user_name):
        role = SilvaTestCase.users[user_name]['role']
        password = SilvaTestCase.users[user_name]['password']
        url = '%s/edit' % self.getRoot().absolute_url()
        self.do_login(browser, url, user_name, password)
        p = re.compile('logout\s+%s' % role)
        p.findall(browser.contents)
        self.failUnless(p, 'The roles do not match')

    def do_make_content(self, user_name, content_type, creator, result):
        browser = Browser()
        try:
            browser
        except HTTPError, err:
            if result is fail_login:
                self.assertEquals(str(err), 'HTTP Error 401: Unauthorized')
            else:
                self.fail()
        self.role_login(browser, user_name)
        try:
            meta_type = browser.getControl(name="meta_type")
        except LookupError:
            if result is fail_nothing_addable:
                self.role_logout(browser)
                return
            self.fail()
        if result is fail_not_addable:
            self.failIf(content_type in meta_type.options, 'on result is fail_not_addable')
        else:
            #import pdb; pdb.set_trace()
            self.failUnless(content_type in meta_type.options, 'on line 47')
            # Create the content 
            browser.getControl(name='meta_type').value = [content_type]
            browser.getControl(name='add_object:method').click()
            browser.getControl(name='field_object_id').value = 'test_content'
            browser.getControl(name='field_object_title').value = 'test content'
            if creator:
               creator(browser)
            browser.getControl(name='add_submit').click()
            self.failUnless('Added %s' % content_type in browser.contents)
            self.failUnless('test_content' in browser.contents)

            # Delete the content
            browser.getControl(name='ids:list').value = ['test_content']
            browser.getControl(name='tab_edit_delete:method').click()
            self.failUnless('Deleted' in browser.contents)

        self.role_logout(browser)
        self.assertEquals('You have been logged out.' in browser.contents, True)

        
class ContentTypeTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                         MixinRole):
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
                              None, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor,'Silva Document',
                              None, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Document',
                              None, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Document',
                              None, success)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Document',
                              None, fail_nothing_addable)
    
    # Silva Folder       
    def test_make_folder(self):
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                            self.fill_create_folderish_form, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Folder',
                            self.fill_create_folderish_form, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Folder',
                            self.fill_create_folderish_form, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Folder',
                            self.fill_create_folderish_form, success)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Folder',
                            self.fill_create_folderish_form, fail_nothing_addable)
    
    def fill_create_folderish_form(self, browser):
        browser.getControl(name='field_policy_name').value = ['Silva Document']
    
    # Silva Publication
    def test_make_publication(self):
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                            self.fill_create_folderish_form, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Publication',
                            self.fill_create_folderish_form, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Publication',
                            self.fill_create_folderish_form, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Publication',
                            self.fill_create_folderish_form, fail_not_addable)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Publication',
                            self.fill_create_folderish_form, fail_nothing_addable)
    
    # Silva AutoTOC
    def test_make_auto_toc(self):
        self.do_make_content(SilvaTestCase.user_manager, 'Silva AutoTOC',
                            self.fill_create_depth_form, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva AutoTOC',
                            self.fill_create_depth_form, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva AutoTOC',
                            self.fill_create_depth_form, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva AutoTOC',
                            self.fill_create_depth_form, success)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva AutoTOC',
                            self.fill_create_depth_form, fail_nothing_addable)

    def fill_create_depth_form(self, browser):
        browser.getControl(name='field_depth').value = '-1'

    # Silva Find
    def test_make_find(self):
        self.do_make_content(SilvaTestCase.user_manager,'Silva Find',
                              None, success)
        self.do_make_content(SilvaTestCase.user_chiefeditor,'Silva Find',
                              None, success)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Find',
                              None, success)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Find',
                              None, fail_not_addable)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Find',
                              None, fail_nothing_addable)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentTypeTestCase))
    return suite
