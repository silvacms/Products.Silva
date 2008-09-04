from urlparse import urlparse

from zope.interface import implements
from zope.publisher.interfaces.http import IHTTPRequest

from AccessControl import ModuleSecurityInfo
from Globals import InitializeClass
from Products.Silva import SilvaPermissions
from Products.Silva.adapters import adapter
from Products.Silva.adapters.interfaces import IPath

from ZPublisher.HTTPRequest import HTTPRequest

module_security = ModuleSecurityInfo('Products.Silva.adapters.path')

import re

frag_re = re.compile("([^\#\?]*)(\?[^\#]*)?(\#.*)?")

from zLOG import LOG,INFO
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
        LOG('urlToPath',INFO,url + "|" + parameters+"|"+query)
        if not path.startswith('/'):
            # try to retain query and fragment information...
            if query:
                path += '?' + query
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
            
        # try to retain path and fragment information..
        if query:
            result += '?' + query
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
            # query and fragment information is in path so will
            # automatically be passed along
            return path
        request = self.request
        #strip off fragment (#) or query before
        #calling physicalPathtoURL, so they don't
        #get converted
        m = frag_re.search(path)
        path = m.group(1)
        query = m.group(2)
        frag = m.group(3)
        # try to retain fragment or query information
        if query:
            path += query
        if frag:
            path += frag
        return path

InitializeClass(PathAdapter)

def __allow_access_to_unprotected_subobjects__(name, value=None):
    return name in ('getPathAdapter')

module_security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                  'getPathAdapter')
def getPathAdapter(request):
    #first test if request provides the zope3 IHTTPRequest interface
    # and if not, fallback to checking if request is an instance of HTTPRequest
    #The interface check allows code to use this pathadapter on other types
    # of httprequest-like objects -- they just have to implement IHTTPRequest
    # SilvaMetadata does this to "fake" a request object, when saving
    # values from request (Binding.setValuesFromRequest)
    assert IHTTPRequest.providedBy(request) or isinstance(request, HTTPRequest)
    return PathAdapter(request)
