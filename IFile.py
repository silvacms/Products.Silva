# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
from IAsset import IAsset

class IFile(IAsset):
    """A File object to encapsulate "downloadable" data
    """
    # MANIPULATORS

    def set_file_data(self, file):
        """Re-upload data for this file object. It will change the 
        content_type, however id, _title, etc. will not change.
        """
        pass
 
    # ACCESSORS

    def get_filename(self):
        """Object's id is filename
        PUBLIC
        """
        pass

    def get_file_size(self):
        """Get the size of the file as it will be downloaded.
        PUBLIC
        """
        pass

    def get_mime_type(self):
        """Get the mime-type for this file.
        PUBLIC
        """
        pass

    def get_download_url(self):
        """Obtain the public URL the public could use to download this file
        PUBLIC
        """
        pass

    def get_download_link(
        self, title_attr='', name_attr='', class_attr='', style_attr=''):
        """Obtain a complete HTML hyperlink by which the public can download
        this file.
        PUBLIC
        """
        pass
                        

