"""
module for parsing dom-nodes or strings to an
object tree based on the classes in 'base.py'.

The ObjectParser instance takes an object
that provides 'mappings' via var(object):
names of tags are mapped to objects which
will be instantiated.

Currently only minidom is supported. 


"""

__author__='Holger P. Krekel <hpk@trillke.net>'
__version__='$Revision: 1.1 $'

from base import Element, Frag, Text

#
# Transformation from Dom to our Nodes
#
class ObjectParser:
    def __init__(self, spec):
        """ initialize ObjectParser with the Element tags
            contained in spec which are later used for
            tagname-to-Object parsing.
        """
        self.spec = spec
        self.typemap = {}
        for x,y in vars(spec).items():
            try:
                if issubclass(y, Element):
                    if hasattr(y, 'xmlname'):
                        x = y.xmlname
                    self.typemap[x]=y
            except TypeError:
                pass

    def parse(self, source):
        """ return xist-like objects parsed from UTF-8 string
            or dom tree.
            
            Fragment contains node objects and unknown a list of unmapped 
            nodes.
        """
        if type(source)==type(u''):
            source = source.encode('UTF8')

        if type(source)==type(''):
            from xml.dom import minidom
            tree = minidom.parseString(source)
        else:
            tree = source # try just using it as dom

        self.unknown = []
        return self._dom2object(*tree.childNodes)

    def _dom2object(self, *nodes):
        """ transform dom-nodes to objects """
        res = Frag()

        for node in filter(None, nodes):
            if node.nodeType == node.ELEMENT_NODE:
                cls = self.typemap.get(node.nodeName)
                if not cls:
                    raise str("warning: unknown element: " + node.nodeName)
                else:
                    childs = self._dom2object(*node.childNodes)
                    attrs = {}
                    if node.attributes:
                        for name, item in node.attributes.items():
                            attrs[name]=Text(item) # .nodeValue)
                    res.append(cls(attrs, *childs))

            elif node.nodeType == node.TEXT_NODE:
                res.append(Text(node.nodeValue))
            else:
                self.unknown.append(node)
        return res
