"""
module for conversion from current 

   RealObjects' 2.11 Pseudo-HTML 
   
       to

   silva (0.8.5) 

This transformation tries to stay close to
how silva maps its xml to html. I am not sure, though,
whether this is a good idea because RealObjects 2.11 
currently let's the user select 'h1' and 'h2' as styles
and we don't want that.

the notation used for the transformation roughly
follows the ideas used with XIST (but is simpler).
Note that we can't use XIST itself as long as 
silva is running on a Zope version that 
doesn't allow python2.2

"""

__author__='holger krekel <hpk@trillke.net>'
__version__='$Revision: 1.11 $'

try:
    from transform.base import Element, Text, Frag
except ImportError:
    from Products.Silva.transform.base import Element, Text, Frag

import silva



class html(Element):
    def convert(self, context, *args, **kwargs):
        """ forward to the body element ... """
        bodytag = self.find('body')[0]
        return bodytag.convert(context, *args, **kwargs)

class head(Element):
    def convert(self, context, *args, **kwargs):
        """ ignore """
        return u''

class body(Element):
    "html-body element"
    def convert(self, context, *args, **kwargs):
        """ contruct a silva_document with id and title
            either from information found in the html-nodes 
            or from the context (where silva should have
            filled in title and id as key/value pairs)
        """
        h2_tag = self.find(tag=h2)
        if not h2_tag:
            rest = self.find()
            title, id = context['title'], context['id']
        else:
            h2_tag=h2_tag[0]
            title = h2_tag.content
            rest = self.find(ignore=h2_tag.__eq__) 
            id = h2_tag.attrs.get('silva_id') or context['id']

        return silva.silva_document(
                silva.title(title),
                silva.doc(
                    rest.convert(context, *args, **kwargs)
                ),
                id = id
            )

class h1(Element):
    def convert(self, *args, **kwargs):
        return silva.heading(
            self.content.convert(*args, **kwargs),
            type='normal'
        )

class h2(Element):
    ""
    def convert(self, *args, **kwargs):
        return silva.heading(
            self.content.convert(*args, **kwargs),
            type="normal"
            )

class h3(Element):
    ""
    def convert(self, *args, **kwargs):
        return silva.heading(
            self.content.convert(*args, **kwargs),
            type="normal"
            )

class h4(Element):
    ""
    def convert(self, *args, **kwargs):
        return silva.heading(
            self.content.convert(*args, **kwargs),
            type="sub"
            )

class h5(Element):
    """ List heading, make sure we find something """
    def convert(self, context, *args, **kwargs):
        """ we try to make out a list-title if possible ...
        """
        post = context.get('post_nodes',[])
        for item in post:
            if hasattr(item, '__class__'):
                cls = item.__class__
                if cls is ul or cls is ol:
                    #print "inserting in list", self.asBytes() 
                    item.content.insert(0, self)
                    return None
                if item.asBytes('utf8').strip():
                    break

        return silva.heading(
            self.content.convert(context, *args, **kwargs),
            type="sub",
            )

class h6(Element):
    def convert(self, *args, **kwargs):
        """ this only gets called if the user erroronaously
            used h6 somewhere 
        """
        return silva.heading(
            self.content.convert(*args, **kwargs),
            type="sub",
            )

class p(Element):
    """ the html p element can contain nodes which are "standalone"
        in silva-xml. 
    """
    def convert(self, *args, **kwargs):
        pre,img,post = self.find_and_partition('img')
        type = self.attrs.get('silva_type', None)
        if pre:
            pre = silva.p(pre.convert(*args, **kwargs), type=type)
        if img:
            img = img.convert(*args, **kwargs)
        if post:
            post = silva.p(post.convert(*args, **kwargs), type=type)

        if not (pre or img or post):
            pre = silva.p(type=type)

        return Frag(
            pre, 
            img,
            post,
        )

class ul(Element):
    """ list conversions, ugh! """
    default_types = ('disc','circle','square','none')
    def convert(self, *args, **kwargs):
        type = self.attrs.get('type', None)
        if type is None:
            type = self.attrs.get('silva_type')
        else:
            type = type.content.lower()
        if type not in self.default_types:
            type = self.default_types[0]

        h5_tag = self.find(tag=h5)
        if not h5_tag:
            title = silva.title()
            rest = self.find(li)
        else:
            title = silva.title(h5_tag[0].content.convert(*args, **kwargs))
            rest = self.find(li, ignore=h5_tag[0].__eq__)
        return silva.list(
            title,
            rest.convert(*args, **kwargs),
            type=type
            )

class ol(ul):
    default_types = ('1','a','i')

class li(Element):
    def convert(self, *args, **kwargs):
        return silva.li(
            self.content.convert(*args, **kwargs),
            )

class b(Element):
    def convert(self, *args, **kwargs):
        return silva.strong(
            self.content.convert(*args, **kwargs),
            )

class i(Element):
    def convert(self, *args, **kwargs):
        return silva.em(
            self.content.convert(*args, **kwargs),
            )

class u(Element):
    def convert(self, *args, **kwargs):
        return silva.underline(
            self.content.convert(*args, **kwargs),
            )

class font(Element):
    def convert(self, *args, **kwargs):
        color = self.attrs.get('color')
        tag = {'aqua': silva.super, 
               'blue': silva.sub,
               }.get(color)
        if tag:
            return tag(
                self.content.convert(*args, **kwargs)
            )
        else:
            return self.content.convert(*args, **kwargs)

class a(Element):
    def convert(self, *args, **kwargs):
        return silva.link(
            self.content.convert(*args, **kwargs),
            url=self.attrs['href']
            )

class img(Element):
    def convert(self, *args, **kwargs):
        return silva.image(
            self.content.convert(*args, **kwargs),
            image_path=self.attrs['src']
            )
class br(Element):
    def convert(self, *args, **kwargs):
        return silva.p(
            "",
            type='normal'
            )

class pre(Element):
    def compact(self):
        return self

    def convert(self, *args, **kwargs):
        return silva.pre(
            self.content.convert(*args, **kwargs)
        )

class table(Element):
    def convert(self, context, *args, **kwargs):
        rows = self.content.find('tr')
        if len(rows)>0:
            cols = len(rows[0].find('td'))
        return silva.table(
                self.content.convert(context, *args, **kwargs),
                columns=self.attrs.get('cols', cols),
                column_info = self.attrs.get('silva_column_info'),
                type=self.attrs.get('silva_type')
            )

class tr(Element):
    def convert(self, context, *args, **kwargs):
        return silva.row(
            self.content.convert(context, *args, **kwargs)
        )

class td(Element):
    def convert(self, *args, **kwargs):
        return silva.field(
            self.content.convert(*args, **kwargs)
        )

"""
current mapping of tags with silva
h1  :  not in use, reserved for (future) Silva publication
       sections and custom templates
h2  :  title
h3  :  heading
h4  :  subhead
h5  :  list title
"""
