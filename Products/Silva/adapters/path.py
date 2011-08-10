# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from urlparse import urlparse

# Zope 3
from zope.publisher.interfaces.http import IHTTPRequest
from five import grok

from App.class_init import InitializeClass

from silva.core.interfaces import ISilvaObject
from silva.core.interfaces.adapters import IPath


class SilvaPathAdapter(grok.Adapter):
    """Adapter to unify the conversion of zope paths to Url Paths
       between the xml-based and widgets-based renderers"""
    grok.context(ISilvaObject)
    grok.implements(IPath)

    def urlToPath(self, url):
        """convert a HTTP URL to a Zope path"""
        raise NotImplemented #(yet)

    def pathToUrlPath(self, path):
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
        parsed_path = urlparse(path)
        if parsed_path.scheme:
            return path
        if not parsed_path.path:
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


class PathAdapter(grok.Adapter):
    """adapter that contains some magic to convert HTTP paths to
        physical paths and back (respecting virtual hosting situations)

        note that this is an adapter for the *request* object, hence
        there's no normal context (instead there's self.request) and
        obviously acquisition can not be used
    """
    grok.context(IHTTPRequest)
    grok.implements(IPath)

    # XXX That's a bit too much
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
        if scheme and scheme not in ['http', 'https']:
            return url
        if netloc and netloc != self.request.environ['HTTP_HOST']:
            # if the url is absolute and the server is not this server, don't
            # convert.
            return url

        # XXX does returning the path if it's relative always work? do we
        # take care to only store 'safe' paths in Silva?
        if not path.startswith('/'):
            # try to retain query and fragment information...
            if query:
                path += '?' + query
            if fragment:
                path += '#' + fragment
            return path

        # physicalPathFromURL breaks in complex virtual hosting situations
        # where incorrect urls are entered by hand, or imported
        try:
            result = '/'.join(self.request.physicalPathFromURL(path))
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

        original_path = urlparse(path)
        if original_path.scheme:
            # This is already a URL
            return path

        url = self.request.physicalPathToURL(original_path.path.split('/'))
        path = urlparse(url)[2]
        # try to retain fragment or query information
        if original_path.query:
            path += '?' + original_path.query
        if original_path.fragment:
            path += '#' + original_path.fragment
        return path


InitializeClass(PathAdapter)


def __allow_access_to_unprotected_subobjects__(name, value=None):
    return name in ('getPathAdapter')


def getPathAdapter(request):
    return IPath(request)
