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

class MixinFieldParameters(object):
    
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

class MixinRoleContent(test_login.MixinLoginLogout):

    item_id = 'test_content'

    def role_logout(self, browser):
        self.do_logout(browser)
        self.assertEquals('You have been logged out.' in browser.contents, True)

    def role_login_edit(self, browser, user_name, result, base=None):
        role = SilvaTestCase.users[user_name]['role']
        password = SilvaTestCase.users[user_name]['password']
        if base is None:
            url = '%s/edit' % self.getRoot().absolute_url()
        else:
            url = '%s/%s/edit' % (self.getRoot().absolute_url(), base)

        # Try login
        try:
            self.do_login(browser, url, user_name, password)
        except HTTPError, err:
            if result is fail_login:
                self.assertEquals(str(err), 'HTTP Error 401: Unauthorized')
            else:
                self.fail()

        # Check the role
        p = re.compile('logout\s+%s' % role)
        p.findall(browser.contents)
        self.failUnless(p, 'The role does not match logout message')

    def do_create_content(self, browser, content_type, creator, result):
        # Test if role has access to no content_types
        try:
            meta_type = browser.getControl(name="meta_type")
        except LookupError:
            if result is fail_nothing_addable:
                return
            self.fail()
        # Test if role has access to content_type
        if result is fail_not_addable:
            self.failIf(content_type in meta_type.options, 'Role can access meta_type')
        else:
            self.failUnless(content_type in meta_type.options, 'Content type is not included as meta_type')
            # Create the content 
            browser.getControl(name='meta_type').value = [content_type]
            browser.getControl(name='add_object:method').click()
            browser.getControl(name='field_object_id').value = self.item_id
            # Check for special fields
            if creator:
               creator(browser)
            browser.getControl(name='add_submit').click()
            self.failUnless('Added %s' % content_type in browser.contents, 'Content type is not included in submit feedback message')
            self.failUnless(self.item_id in browser.contents)

    def do_delete_content(self, browser):
        # Delete the content
        browser.getControl(name='ids:list').value = [self.item_id]
        browser.getControl(name='tab_edit_delete:method').click()
        self.failUnless('Deleted' in browser.contents)

    def do_make_content(self, user_name, content_type, creator, result, base=None, delete=True):
        """
            this method takes a role, logs the user (role) in, selects a content
            type, makes the content type, then deletes the content type, and 
            then logs the user out
        """
        browser = Browser()
        self.role_login_edit(browser, user_name, result, base=base)
        if result is fail_login:
            return
        self.do_create_content(browser, content_type, creator, result)
        if result is success and delete:
            self.do_delete_content(browser)
        self.role_logout(browser)

    def do_login_and_delete_content(self, user_name, result, base=None):
        browser = Browser()
        self.role_login_edit(browser, user_name, result, base=base)
        if result is fail_login:
            return
        self.do_delete_content(browser)
        self.role_logout(browser)

class ContentTypeTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                          MixinRoleContent, MixinFieldParameters):
    """
       make a content type as each role of silva
       login role
       select content type
       make content type
       delete document
       logout role
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
     
    # Silva Indexer
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

class ContentTypeInFolderTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                                       MixinRoleContent, MixinFieldParameters):
    """
       make a content type then enter the content type and make the same
         content type as each role of silva
       login role
       select folder
       make folder
       enter folder
       make folder
       delete folder
       navigate up one level
       delete folder
       logout role
    """

    def test_folder_in_folder(self):
        """
            create folder, create folder in folder, delete the folder,
            delete folder
        """
        # make a folder as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Folder',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Folder',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Folder',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Folder',
                             self.fill_create_folderish_field, fail_nothing_addable, delete=False)
        # delete folder
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

    
    def test_publication_in_folder(self):
        """
            create a folder, create a publication in the folder, delete the 
            publication, delete the folder
        """
        # make a folder as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Publication',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Publication',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Publication',
                             self.fill_create_folderish_field, fail_not_addable, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Publication',
                             self.fill_create_folderish_field, fail_nothing_addable, base=self.item_id)
        # delete folder
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)
    
    def test_document_in_folder(self):
        """
            create a folder, create a document in folder, delete the document,
            delete the folder
        """
        # make a folder as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager,'Silva Document',
                              self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor,'Silva Document',
                              self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor,'Silva Document',
                              self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author,'Silva Document',
                              self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Document',
                             self.fill_create_folderish_field, fail_nothing_addable, base=self.item_id)
        # delete folder
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

    def test_image_in_folder(self):
        """
            create a folder, create an image in the folder, delete the image,
            delete the folder
        """
        # make a folder as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Image',
                             self.fill_create_image_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Image',
                             self.fill_create_image_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Image',
                             self.fill_create_image_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Image',
                             self.fill_create_image_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Image',
                             self.fill_create_folderish_field, fail_nothing_addable, base=self.item_id)
        # delete folder
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)
    
    def test_file_in_folder(self):
        """
            create a folder, create a file in the folder, delete the file,
            delete the folder
        """
        # make a folder as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva File',
                             self.fill_create_file_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva File',
                             self.fill_create_file_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva File',
                             self.fill_create_file_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva File',
                             self.fill_create_file_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva File',
                             self.fill_create_folderish_field, fail_nothing_addable, base=self.item_id)
        # delete folder
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)
    
    def test_ghost_in_folder(self):
        """
            create a folder, create a ghost in the folder, delete the ghost,
            delete the folder
        """
        # make folder as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Ghost',
                             self.fill_create_folderish_field, fail_nothing_addable, base=self.item_id)
        # delete folder
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)
    
    def test_ghost_folder_in_folder(self):
        """
            create a folder, create a ghost folder in the folder, delete the 
            ghost folder, delete the folder
        """
        # make folder as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, fail_not_addable, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Ghost Folder',
                             self.fill_create_folderish_field, fail_nothing_addable, base=self.item_id)
        # delete folder 
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

    def test_indexer_in_folder(self):
        """
            create an folder, create and indexer in the folder, delete the
            indexer, delete the folder
        """
        # make a folder as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Indexer',
                             self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Indexer',
                             self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Indexer',
                             self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Indexer',
                             self.fill_create_title_field, fail_not_addable, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Indexer',
                             self.fill_create_title_field, fail_nothing_addable, base=self.item_id)
        # delete folder
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

    def test_link_in_folder(self):
        """
            create a folder, create an link in the folder, delete the 
            link, delete the folder
        """
        # make folder as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Link',
                             self.fill_create_link_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Link',
                             self.fill_create_link_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Link',
                             self.fill_create_link_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Link', 
                             self.fill_create_link_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Link',
                             self.fill_create_folderish_field, fail_nothing_addable, base=self.item_id)
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)
    
    def test_autoTOC_in_folder(self):
        """
            create folder, create autoTOC in folder, delete the autoTOC,
            delete folder
        """

        # make folder as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva AutoTOC',
                            self.fill_create_depth_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva AutoTOC',
                            self.fill_create_depth_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva AutoTOC',
                            self.fill_create_depth_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva AutoTOC',
                            self.fill_create_depth_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva AutoTOC',
                            self.fill_create_depth_field, fail_nothing_addable, base=self.item_id)
        # delete folder
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

class ContentTypeInPublicationTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                                       MixinRoleContent, MixinFieldParameters):
    """
       make a content type then enter the content type and make the same
         content type as each role of silva
       login role
       select folder
       make folder
       enter folder
       make folder
       delete folder
       navigate up one level
       delete folder
       logout role
    """

    def test_publication_in_publication(self):
        """
            create publication, create publication in publication, delete the publication,
            delete publication
        """
        # make publication as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Publication',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Publication',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Publication',
                             self.fill_create_folderish_field, fail_not_addable, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Publication',
                             self.fill_create_folderish_field, fail_nothing_addable, base=self.item_id)
        # delete publication
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

    def test_folder_in_publication(self):
        """
            create publication, create folder in publication, delete the folder,
            delete publication
        """
        # make publication as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Folder',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Folder',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Folder',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Folder',
                             self.fill_create_folderish_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Folder',
                             self.fill_create_folderish_field, fail_nothing_addable, base=self.item_id)
        # delete publication
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

    def test_document_in_publication(self):
        """
            create publication, create document in publication, delete the document,
            delete publication
        """
        # make publication as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Document',
                             self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Document',
                             self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Document',
                             self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Document',
                             self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Document',
                             self.fill_create_title_field, fail_nothing_addable, base=self.item_id)
        # delete publication
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

    def test_image_in_publication(self):
        """
            create publication, create image in publication, delete the image,
            delete publication
        """
        # make publication as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Image',
                             self.fill_create_image_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Image',
                             self.fill_create_image_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Image',
                             self.fill_create_image_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Image',
                             self.fill_create_image_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Image',
                             self.fill_create_image_fields, fail_nothing_addable, base=self.item_id)
        # delete publication
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

    def test_file_in_publication(self):
        """
            create publication, create file in publication, delete the file,
            delete publication
        """
        # make publication as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva File',
                             self.fill_create_file_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva File',
                             self.fill_create_file_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva File',
                             self.fill_create_file_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva File',
                             self.fill_create_file_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva File',
                             self.fill_create_file_fields, fail_nothing_addable, base=self.item_id)
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

    def test_ghost_in_publication(self):
        """
            create publication, create ghost in publication, delete the ghost,
            delete publication
        """
        # make publication as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Ghost',
                             self.fill_create_ghost_url_field, fail_nothing_addable, base=self.item_id)
        # delete publication
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

    def test_ghost_folder_in_publication(self):
        """
            create publication, create ghost folder in publication, delete the ghost folder,
            delete publication
        """
        # make publication as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, fail_not_addable, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, fail_nothing_addable, base=self.item_id)
        # delete publication
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

    def test_indexer_in_publication(self):
        """
            create publication, create indexer in publication, delete the indexer,
            delete publication
        """
        # make a publication as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Indexer',
                             self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Indexer',
                             self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Indexer',
                             self.fill_create_title_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Indexer',
                             self.fill_create_title_field, fail_not_addable, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Indexer',
                             self.fill_create_title_field, fail_nothing_addable, base=self.item_id)
        # delete folder
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

    def test_link_in_publication(self):
        """
            create publication, create link in publication, delete the link,
            delete publication
        """
        # make publication as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Link',
                             self.fill_create_link_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Link',
                             self.fill_create_link_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Link',
                             self.fill_create_link_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva Link', 
                             self.fill_create_link_fields, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Link',
                             self.fill_create_folderish_field, fail_nothing_addable, base=self.item_id)
        # delete folder
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

    def test_autoTOC_in_publication(self):
        """
            create publication, create autoTOC in publication, delete the autoTOC,
            delete publication
        """
        # make publication as manager
        self.do_make_content(SilvaTestCase.user_manager, 'Silva Publication',
                             self.fill_create_folderish_field, success, delete=False)
        # go into content type and add new content type
        self.do_make_content(SilvaTestCase.user_manager, 'Silva AutoTOC',
                            self.fill_create_depth_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva AutoTOC',
                            self.fill_create_depth_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_editor, 'Silva AutoTOC',
                            self.fill_create_depth_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_author, 'Silva AutoTOC',
                            self.fill_create_depth_field, success, base=self.item_id)
        self.do_make_content(SilvaTestCase.user_reader, 'Silva AutoTOC',
                            self.fill_create_depth_field, fail_nothing_addable, base=self.item_id)
        # delete folder
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentTypeTestCase))
    #suite.addTest(unittest.makeSuite(ContentTypeInFolderTestCase))
    #suite.addTest(unittest.makeSuite(ContentTypeInPublicationTestCase))
    return suite
