"""
module for providing base xml element/attribute classes.

a namespace (silva and html currently) uses the default
behaviour of the elements contained here.

Note: 
   There is no xml-namespace support up to now.

   The actual transformations are in separate 
   module and don't depend on Zope or Silva. They do
   depend on a DOM-parser (and thus share the
   dependcy on PyXML.

the scheme used for the transformation roughly
follows the ideas used with XIST.  Note that we
can't use XIST itself (which is the upgrade idea)
as long as silva is running on a Zope version that 
doesn't allow python2.2 or better.

"""

__author__='Holger P. Krekel <hpk@trillke.net>'
__version__='$Revision: 1.5 $'

# look ma, i only have these dependencies 
# and with python2.2 even they would vanish
# that's because we work with python objects trees
# instead of a proprietary format :-)

import re 
from UserList import UserList as List
from UserDict import UserDict as Dict

class Node:
    def _matches(self, tag):
        if type(tag) in (type(''),type(u'')):
            return self.name()==tag
        elif tag is None:
            return 1
        else:
            return self.__class__ == tag

    def __eq__(self, other):
        raise "not implemented, override in inheriting class"

    def name(self):
        return getattr(self, 'xmlname', self.__class__.__name__)

    def conv(self):
        return self.convert({})

class Frag(Node, List):
    """ Fragment of Nodes (basically list of Nodes)"""
    def __init__(self, *content):
        List.__init__(self)
        map(self.append, content)

    def __eq__(self, other):
        try:
            if len(self)!=len(other):
                return 0
            for x,y in zip(self, other):
                if not x == y:
                    return 0
        except:
            return 0
        return 1

    def __ne__(self, other):
        return not self==other

    def append(self, *others):
        for other in others:
            if not other:
                continue
            if isinstance(other, Frag) or \
               type(other) == type(()) or \
               type(other) == type([]):
                List.extend(self, other)
            else:
                List.append(self, other)

    def convert(self, context, *args, **kwargs):
        frag = self.__class__()
        pre = Frag()
        post = Frag(self)
        while post:
            node = post.pop(0)
            context['pre_nodes']=pre
            context['post_nodes']=post
            frag.append(node.convert(context, *args, **kwargs))
            pre.append(node)
        return frag

    def extract_text(self):
        l = []
        for node in self:
            l.append(node.extract_text())
        return u''.join(l)


    def compact(self):
        node = self.__class__()
        for child in self:
            cchild = child.compact()
            node.append(cchild)
        return node

    def find(self, tag=None, ignore=lambda x: None):
        node = Frag()
        for child in self:
            if not ignore(child) and child._matches(tag):
                node.append(child)
        return node

    def find_and_partition(self, tag):
        pre,match,post = Frag(), Element(), Frag()
        allnodes = self[:]

        while allnodes:
            child = allnodes.pop(0)
            if child._matches(tag):
                match = child
                post = Frag(allnodes)
                break
            pre.append(child)
        return pre,match,post

    def asBytes(self, encoding='UTF-8'):
        l = []
        for child in self:
            l.append(child.asBytes(encoding))
        return "".join(l)

class Attrs(Dict):
    def __getattr__(self, name):
        if name.startswith('_'):
            name = name[1:]
            try:
                return self[name]
            except:
                raise AttributeError, "attribute %s non-existent" % name
    def __contains__(self, name):
        if name.startswith('_'):
            name = name[1:]
            return name in self

class Element(Node):
    def __init__(self, *content, **attrs):
        self.attrs = Attrs()
        newcontent = []
        for child in content:
            try:
                for name, value in child.items():
                    self.attrs[name]=value
            except:
                if type(child) in (type(''),type(u'')):
                    child = Text(child)
                newcontent.append(child)
        self.content = Frag(*newcontent)
        for name, value in attrs.items():
            if value is not None:
                self.attrs[name]=value

    def __eq__(self, other):
        try:
            if self.attrs == other.attrs and self.content==other.content:
                return 1
        except:
            pass

    def __ne__(self, other):
        return not self==other

    def __nonzero__(self):
        return self.name()!=Element.__name__

    def compact(self):
        node = self.__class__()
        node.content = self.content.compact()
        node.attrs = self.attrs.copy()
        return node

    def extract_text(self):
        return self.content.extract_text()

    def isEmpty(self):
        tmp = self.compact()
        return len(tmp.content.find())==0

    def find(self, *args, **kwargs):
        return self.content.find(*args, **kwargs)

    def find_and_partition(self, *args, **kwargs):
        return self.content.find_and_partition(*args, **kwargs)

    def convert(self, *args, **kwargs):
        return self

    def asBytes(self, encoding='UTF-8'):
        """ return canonical xml-conform representation  """
        attrlist=[]
        for name, value in self.attrs.items():
            if value is None:
                continue

            name = name.encode(encoding)
            if value:
                if hasattr(value, 'asBytes'):
                    value = value.asBytes(encoding)
                elif type(value)==type(u''):
                    value = value.encode(encoding)
                else:
                    value = value

                attrlist.append('%s="%s"' % (name, value))
            else:
                attrlist.append(name)

        subnodes = self.content.asBytes(encoding)
        attrlist = " ".join(attrlist)

        name = self.name().encode(encoding)
        
        if attrlist:
            start = '<%(name)s %(attrlist)s' % locals()
        else:
            start = '<' + name.encode(encoding)
        if subnodes: 
                return '%(start)s>%(subnodes)s</%(name)s>' % locals()
        else:
            return '%(start)s/>' % locals()

# BEGIN special character handling
class CharRef:
    pass

class quot(CharRef): "quotation mark = APL quote, U+0022 ISOnum"; codepoint = 34
class amp(CharRef): "ampersand, U+0026 ISOnum"; codepoint = 38
class lt(CharRef): "less-than sign, U+003C ISOnum"; codepoint = 60
class gt(CharRef): "greater-than sign, U+003E ISOnum"; codepoint = 62
class apos(CharRef): "apostrophe mark, U+0027 ISOnum"; codepoint = 39

class _escape_chars:
    def __init__(self):
        self.escape_chars = {}
        for _name, _obj in globals().items():
            try:
                if issubclass(_obj, CharRef) and _obj is not CharRef:
                    self.escape_chars[unichr(_obj.codepoint)] = u"&%s;" % _name
            except TypeError:
                continue
        self.charef_rex = re.compile(u"|".join(self.escape_chars.keys()))
            
    def _replacer(self, match):
        return self.escape_chars[match.group(0)]

    def __call__(self, ustring):
        return self.charef_rex.sub(self._replacer, ustring)

escape_chars = _escape_chars()

# END special character handling

class CharacterData(Node):
    def __init__(self, content=u""):
        if type(content)==type(''):
            content = unicode(content)
        self.content = content

    def extract_text(self):
        return self.content

    def convert(self, *args, **kwargs):
        return self

    def __eq__(self, other):
        try:
            return self.content == other.content
        except AttributeError:
            return self.content == other
    
    def __ne__(self, other):
        return self==other

    def __hash__(self):
        return hash(self.content)

    def __len__(self):
        return len(self.content)

    def asBytes(self, encoding):
        content = escape_chars(self.content)
        return content.encode(encoding)


class Text(CharacterData):
    def compact(self):
        if self.content.isspace():
            return None
        else:
            return self

