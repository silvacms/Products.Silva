"""
 simple module for conversions 

 workflow:

 - you set a loader for a conversion (source_vt, target_vt)

 - you ask for a converter for a (source_vt, target_vt) 
   mapping. 

 versioned type identifiers
 ---------------------------

 the above source and target arguments are "versioned type
 identifiers".  Additionally they can have a representation
 type with   such as 'minidom:xml-1.0' or 
 'silvaxml-0.9.0', 'docma-0.5', 
 'eonprohtml-1.', 
 'parsedxml', 'minidom',
 'unicode' or whatever.

 a versioned identifier is an identifier with an
 appended version string such as '-1.0' or '-0.8.7' etc.

 so a versioned identifier string always has the format.

     some_id-x.y.z

 Each versioned identifier implies exactly one representation. 
 This restriction is neccesary to allow sane chaining of 
 converters. 
"""

from __future__ import nested_scopes

class UnknownId(Exception):
    pass

class UnknownVersion(Exception):
    pass

class NoConversionPath(Exception):
    pass

class FormatError(Exception):
    pass

def split_ident(string):
    """split identifier string into identifier part
    and a version tuple.
    """
    try:
        id, version = string.split('-')
        version = tuple(version.split('.'))
    except ValueError:
        raise FormatError(string)
    return id, version

class ChainedConv:

    def __init__(self, convlist):
        self.convlist = convlist

    def __call__(self, res):
        return reduce(lambda x,y: y(x), self.convlist, res)

class Registry:
    convmap = {} # map: id, version -> (id,version -> loader) 

    def _versioned_idents(self):
        """return a sequence of all source/target items."""
        l = []
        for item in self.convmap.items():
            l.append(item[0])
            map(l.append, item[1].keys())
        return l

    def _check_idversion(self, id, version):
        id_exists = 0
        for i, v in self._versioned_idents():
            if id == i:
                id_exists=1
                if version == v:
                    return
        if id_exists:
            raise UnknownVersion("%s-%s" % (id, ".".join(version)))
        else:
            raise UnknownId(id)

    def get_converter_list(self, source, target):
        """return a list of converters.

        source and target are versioned types of the form
             someidentifier-x.y.z
        where x, y, z are version numbers
        """

        s = split_ident(source)
        t = split_ident(target)

        self._check_idversion(*s)
        self._check_idversion(*t)

        path = find_shortest_path(self.convmap, s, t)
        if not path:
            raise NoConversionPath(source, target)

        convlist = []
        for current, next in zip(path, path[1:]):
            loader = self.convmap.get(current).get(next)
            convlist.append(loader(current, next))
        return convlist

    def get_converter(self, source, target):
        """return a callable converter. 

        source and target are versioned types. 
        If neccessary a list of converts is invoked
        for performing the conversion from 'source'
        to 'target'. 
        """

        convlist = self.get_converter_list(source, target)
        conv = ChainedConv(convlist)
        return conv

    def set_loader(self, loader, source, target):
        """set a loader for a specific conversion.

        loader must be a callable object.
        source and target are versioned type identifiers.

        The loader will get called with two tuples
        containing (source_id, source_version) and
        (target_id, target_version) respectively.

        This allows *one* loader to care for multiple
        versions. 
        """

        assert callable(loader)

        src = split_ident(source)
        tar = split_ident(target)

        self.convmap.setdefault(src, {})[tar]=loader

_registry = Registry()

set_loader = _registry.set_loader
get_converter = _registry.get_converter


def find_shortest_path(graph, start, end, path=[]):
    """ courtesy of Guido van Rossum in 
    http://www.python.org/doc/essays/graphs.html
    """
    #print "start", start, "end", end

    path = path + [start]
    if start == end:
        return path
    if not graph.has_key(start):
        return []
    shortest = []
    for node in graph[start].keys():
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest
