from urlparse import urlparse

# Zope 3
from zope.interface import implements
from zope.publisher.interfaces.http import IHTTPRequest

from AccessControl import ModuleSecurityInfo
from Globals import InitializeClass
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core.conf import component
from silva.core.interfaces import ISilvaObject
from silva.core.interfaces.adapters import IPath

module_security = ModuleSecurityInfo('Products.Silva.adapters.path')

import re

frag_re = re.compile("([^\#\?]*)(\?[^\#]*)?(\#.*)?")
URL_PATTERN = r'(((http|https|ftp|news)://([A-Za-z0-9%\-_]+(:[A-Za-z0-9%\-_]+)?@)?([A-Za-z0-9\-]+\.)+[A-Za-z0-9]+)(:[0-9]+)?(/([A-Za-z0-9\-_\?!@#$%^&*/=\.]+[^\.\),;\|])?)?|(mailto:[A-Za-z0-9_\-\.]+@([A-Za-z0-9\-]+\.)+[A-Za-z0-9]+))'
_url_match = re.compile(URL_PATTERN)

class SilvaPathAdapter(component.Adapter):
    """Adapter to unify the conversion of zope paths to Url Paths
       between the xml-based and widgets-based renderers"""
    silvaconf.context(ISilvaObject)
    implements(IPath)
    
    def pathToUrl(self, path):
        """ Translate a zope path to a Url."""
        """ this was previously _linkHelper / rewriteUrl """
        """ what sorts of links do we need:
         1) absolute url
         2) query
         3) bookmark
         4) relative path within the same container
         5) relative path within a child of the same container
         6) path with the same root, different container
         virtualhosting:
         7) (same as 4)
         8) (same as 5)
         9) path within silva, different vhost
         
         given:
         /silva/
               /rootc/
                     /doc
                     /next
                     /c/
                       /cdoc
        A link in /silva/rootc/c/cdoc to /silva/rootc/next will be stored as /silva/rootc/next
           and publicly rendered as /silva/rootc/next
        -- this is fine in the nonvhosting context
        A link in /silva/rootc/next to /silva/rootc/c/cdoc will be stored as c/cdoc (relative)
           and publicly rendered as c/cdoc
        -- this is also find in both contexts (nonvosted, vhosted)
        
        -- reasons for using absolute_url:
           -- think: saving a relative path to an object only accessible
              through acquisition (is this bad)? -- absoluteurl will
              cleanup the path
           -- to add on the ++preview++ layer, so absolute urls automatically 
              stay within that layer
         """
        # If path is empty (can it be?), just return it
        if path == '':
            return path
        # If it is a url already, return it:
        if _url_match.match(path):
            return path
        # Is it simply a query or anchor fragment? If so, return it
        if path[0] in ['?', '#']:
            return path
        # It is not an URL, query or anchor, so treat it as a path.
        # If it is a relative path, treat is as such:
        if not path.startswith('/'):
            container = self.context.get_container()
            return self._convertPath(container.absolute_url() + '/' + path)
        # If it is an absolute path, try to traverse it to
        # a Zope/Silva object and get the URL for that.
        splitpath = [p.encode('ascii','ignore') for p in path.split('/') ]
        obj = self.context.restrictedTraverse(splitpath, None)
        if obj is None:
            # Was not found, maybe the link is broken, but maybe it's just 
            # due to virtual hosting situations or whatever.
            return self._convertPath(path)
        if hasattr(obj.aq_base, 'absolute_url'):
            # There are some cases where the object we find 
            # does not have the absolute_url method.
            return obj.absolute_url()
        # In all other cases:
        return self._convertPath(path)
    
    def _convertPath(self, path):
        """if it's not an absolute url, run it through the
          IPath adapter on the REQUEST to take into account
          virtual hosting situations"""
        if urlparse(path)[0]:
            return path
        pad = IPath(self.context.REQUEST)
        return pad.pathToUrlPath(path)

class PathAdapter(component.Adapter):
    """adapter that contains some magic to convert HTTP paths to
        physical paths and back (respecting virtual hosting situations)
        
        note that this is an adapter for the *request* object, hence
        there's no normal context (instead there's self.request) and
        obviously acquisition can not be used
    """

    silvaconf.context(IHTTPRequest)
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
        url = request.physicalPathToURL(path.split('/'))
        path = urlparse(url)[2]
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
