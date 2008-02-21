from FunctionalTestMixin import *
from Products.Five.testbrowser import Browser

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
                             self.fill_create_folderish_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Publication',
                             self.fill_create_folderish_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Publication',
                             self.fill_create_folderish_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_author, 'Silva Publication',
                             self.fill_create_folderish_field, fail_not_addable, base='test_content')
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Publication',
                             self.fill_create_folderish_field, fail_nothing_addable, base='test_content')
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
                             self.fill_create_folderish_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Folder',
                             self.fill_create_folderish_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Folder',
                             self.fill_create_folderish_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_author, 'Silva Folder',
                             self.fill_create_folderish_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Folder',
                             self.fill_create_folderish_field, fail_nothing_addable, base='test_content')
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
                             self.fill_create_title_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Document',
                             self.fill_create_title_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Document',
                             self.fill_create_title_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_author, 'Silva Document',
                             self.fill_create_title_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Document',
                             self.fill_create_title_field, fail_nothing_addable, base='test_content')
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
                             self.fill_create_image_fields, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Image',
                             self.fill_create_image_fields, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Image',
                             self.fill_create_image_fields, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_author, 'Silva Image',
                             self.fill_create_image_fields, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Image',
                             self.fill_create_image_fields, fail_nothing_addable, base='test_content')
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
                             self.fill_create_file_fields, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva File',
                             self.fill_create_file_fields, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_editor, 'Silva File',
                             self.fill_create_file_fields, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_author, 'Silva File',
                             self.fill_create_file_fields, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_reader, 'Silva File',
                             self.fill_create_file_fields, fail_nothing_addable, base='test_content')
        # delete publication
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
                             self.fill_create_ghost_url_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_author, 'Silva Ghost',
                             self.fill_create_ghost_url_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Ghost',
                             self.fill_create_ghost_url_field, fail_nothing_addable, base='test_content')
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
                             self.fill_create_ghost_url_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_author, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, fail_not_addable, base='test_content')
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Ghost Folder',
                             self.fill_create_ghost_url_field, fail_nothing_addable, base='test_content')
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
                             self.fill_create_title_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Indexer',
                             self.fill_create_title_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Indexer',
                             self.fill_create_title_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_author, 'Silva Indexer',
                             self.fill_create_title_field, fail_not_addable, base='test_content')
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Indexer',
                             self.fill_create_title_field, fail_nothing_addable, base='test_content')
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
                             self.fill_create_link_fields, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva Link',
                             self.fill_create_link_fields, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_editor, 'Silva Link',
                             self.fill_create_link_fields, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_author, 'Silva Link', 
                             self.fill_create_link_fields, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_reader, 'Silva Link',
                             self.fill_create_folderish_field, fail_nothing_addable, base='test_content')
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
                            self.fill_create_depth_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_chiefeditor, 'Silva AutoTOC',
                            self.fill_create_depth_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_editor, 'Silva AutoTOC',
                            self.fill_create_depth_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_author, 'Silva AutoTOC',
                            self.fill_create_depth_field, success, base='test_content')
        self.do_make_content(SilvaTestCase.user_reader, 'Silva AutoTOC',
                            self.fill_create_depth_field, fail_nothing_addable, base='test_content')
        # delete folder
        self.do_login_and_delete_content(SilvaTestCase.user_manager, success)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentTypeInPublicationTestCase))
    return suite
