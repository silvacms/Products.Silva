from urlparse import urlparse

from zope.interface import implements

from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Globals import InitializeClass
from Products.Silva import SilvaPermissions
from Products.Silva.adapters import adapter
from Products.Silva.adapters.interfaces import IPath

from ZPublisher.HTTPRequest import HTTPRequest

module_security = ModuleSecurityInfo('Products.Silva.adapters.path')

class PathAdapter(adapter.Adapter):
    """adapter that contains some magic to convert HTTP paths to
        physical paths and back (respecting virtual hosting situations)
        
        note that this is an adapter for the *request* object, hence
        there's no normal context (instead there's self.request) and
        obviously acquisition can not be used
    """

    implements(IPath)
    __allow_access_to_unprotected_subobjects__ = True

    def __init__(self, request):
        self.request = request

    def urlToPath(self, url):
        """convert a HTTP URL to a Zope path

            the HTTP URL can be a complete URL, an absolute URL from the
            root of the virtual host, or a relative path (the latter will
            be returned untouched)
        """
        scheme, netloc, path, parameters, query, fragment = urlparse(url)
        # XXX does returning the path if it's relative always work? do we
        # take care to only store 'safe' paths in Silva?
        if not path.startswith('/'):
            # try to retain fragment information...
            if fragment:
                path += '#' + fragment
            return path
        request = self.request
        
        # physicalPathFromURL breaks in complex virtual hosting situations
        # where incorrect urls are entered by hand, or imported
        try:
            result = '/'.join(request.physicalPathFromURL(path))
        except ValueError:
            result = path
            
        # try to retain fragment information..
        if fragment:
            result += '#' + fragment
        return result
    
    def pathToUrlPath(self, path):
        """convert a Zope physical path to a URL

            returns an absolute path relative from the HTTP virtual host
            root, unless the path is relative, then it just returns it
            as is 
        """
        # XXX does returning the path if it's relative always work? do we
        # take care to only store 'safe' paths in Silva?
        if not path.startswith('/'):
            # fragment information is in path so will automatically be
            # passed along
            return path
        request = self.request
        url = request.physicalPathToURL(path.split('/'))
        scheme, netloc, path, parameters, query, fragment = urlparse(url)
        # try to retain fragment information
        if fragment:
            path += '#' + fragment
        return path

InitializeClass(PathAdapter)

def __allow_access_to_unprotected_subobjects__(name, value=None):
    return name in ('getPathAdapter')

module_security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                  'getPathAdapter')
def getPathAdapter(request):
    assert isinstance(request, HTTPRequest)
    return PathAdapter(request)
