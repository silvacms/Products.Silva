# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $

# Installation-wide configuration options:


# Silva File options.
#
# These options maybe overrided on a per site basis
# by an FilesService object named 'service_files'.
#
FILESYSTEM_STORAGE_ENABLED = 0       # Set to 1 to enable external storage.

FILESYSTEM_PATH = 'var/repository'   # Path to store files relative to
                                     # Zope's INSTANCE_HOME. For security
                                     # reasons, only alphanumeric and '/'
                                     # characters are allowed. However, a 
                                     # leading '/' will be ignored.