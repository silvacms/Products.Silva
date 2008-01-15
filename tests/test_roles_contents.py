from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

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

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentTypeTestCase))
    return suite
