##try:

from Products.FileSystemSite.DirectoryView import registerDirectory, \
     registerFileExtension
from Products.FileSystemSite.FSImage import FSImage
from Products.FileSystemSite.DirectoryView import manage_addDirectoryView
from Products.FileSystemSite.utils import minimalpath, expandpath
from Products.FileSystemSite.FSDTMLMethod import FSDTMLMethod
from Products.FileSystemSite.FSPageTemplate import FSPageTemplate
    
# can enable this to make it work with CMFCore instead of FileSystemSite
# except some freakish behavior if you install both (and install/uninstall
# Silva a few times) though.
##except ImportError:
##    from Products.CMFCore.DirectoryView import registerDirectory,\
##         registerFileExtension
##    from Products.CMFCore.FSImage import FSImage
##    from Products.CMFCore.DirectoryView import manage_addDirectoryView
##    from Products.CMFCore.utils import minimalpath, expandpath
##    from Products.CMFCore.FSDTMLMethod import FSDTMLMethod
##    from Products.CMFCore.FSPageTemplate import FSPageTemplate
