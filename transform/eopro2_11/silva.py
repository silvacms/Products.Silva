"""
module for conversion from current silva (0.8.5) to
RealObjects' EOPRO2.11 Pseudo-HTML.

the notation used for the transformation roughly
follows the ideas used with XIST (but simpler).  
Note that we can't use XIST itself as long as 
silva is running on a Zope version that 
doesn't allow python2.2.1

"""

__author__='holger krekel <hpk@trillke.net>'
__version__='$Revision: 1.12 $'

try:
    from transform.base import Element, Frag, Text
except ImportError:
    from Products.Silva.transform.base import Element, Frag, Text

import html

_attr_origin=u'silva_origin'
_attr_prefix=u'silva_'

# special attribute used for heuristics when transforming
# back to silva-xml

class SilvaElement(Element):
    def backattr(self):
        """ return dictionary with back attributes
            these attributes are later used for 
            the transformation from html to silvaxml.
        """
        attrs = {}
        for name, value in self.attrs.items():
            name = u'silva_'+name
            attrs[name]=value

        attrs[u'silva_origin']=self.name()
        return attrs

    def convert(self, context):
        """ for transformation of silva nodes to 
            html often we just want the content of 
            the node without the surrounding tags. 
        """
        return self.content.convert(context)

# -------------------------------------------------
# SILVA-XML Version 1 conversions to html
# -------------------------------------------------

class silva_document(SilvaElement):
    def convert(self, context):
        node_title = self.find(tag=title)[0]
        node_body = self.find(tag=doc)[0]

        body = html.body(
            html.h2(node_title.convert(context), 
                    silva_origin='silva_document',
                    silva_id=self.attrs._id
                    ),
            node_body.convert(context),
            self.backattr()
            )
        return body

class title(SilvaElement): 
    """ us used with documents, list and tables (i guess) """

class doc(SilvaElement):
    """ subtag of silva_document """

class heading(SilvaElement):
    def convert(self, context):
        level = self.attrs['type'].content
        h_tag = {u'normal' : html.h3, u'sub': html.h4 }.get(level, html.h3)

        return h_tag(
            self.content.convert(context),
            )

class p(SilvaElement):
    def convert(self, *args, **kwargs):
        return html.p(
            self.content.convert(*args, **kwargs),
            silva_type=self.attrs.get('type')
            )

class dlist(SilvaElement):
    """ Simple lists """

    def convert(self, context):
        #print "checking", self.asBytes()
        listtype = self.attrs.get('type', 'normal')

        list_title = self.find(tag=title)[0]
        if len(list_title.compact().content)>0:
            list_title = html.h5(list_title.content.convert(context))
        else:
            list_title=Text('')

        li_list = []
        for tag,nexttag in zip(self.content, self.content[1:]):
            if tag.name()=='dt' and nexttag.name()=='dd':
                li_list.append(
                    html.li(
                        tag.convert(context), 
                        ' ',
                        nexttag.convert(context)
                    )
                )
        return html.ul(list_title,
                       *li_list
                       )

class dt(SilvaElement):
    """dlist define term"""
    def convert(self, context):
        return html.font(self.content.convert(context), color='green')

class dd(SilvaElement):
    """dlist define term"""
    def convert(self, context):
        return self.content.convert(context)

class list(SilvaElement):
    """ Simple lists """
    def convert(self, context):
        listtype = self.attrs.get('type')
        listtype = listtype and listtype.content.lower() or u'none'

        attrs = {}
        if listtype in ['1','i','a']:
            tag = html.ol
            attrs[u'type']=listtype
        elif listtype in (u'disc',u'square',u'circle'):
            tag = html.ul
        else:
            tag = html.ul

        title_tag = self.find(tag=title)[0]

        if len(title_tag.compact().content)>0:
            title_content = html.h5(title_tag.convert(context))
        else:
            title_content=Text('')

        return Frag(
            title_content,
            tag(
                self.find(ignore=title_tag.__eq__).compact().convert(context),
                attrs,
                silva_type=listtype,
                )
            )

class nlist(list):
    pass

class li(SilvaElement):
    """ list items """
    def convert(self, *args, **kwargs):
        return html.li(
            self.content.convert(*args, **kwargs)
            )

class strong(SilvaElement):
    def convert(self, *args, **kwargs):
        return html.b(
            self.content.convert(*args, **kwargs)
            )

class underline(SilvaElement):
    def convert(self, *args, **kwargs):
        return html.u(
            self.content.convert(*args, **kwargs)
            )

class em(SilvaElement):
    def convert(self, *args, **kwargs):
        return html.i(
            self.content.convert(*args, **kwargs)
            )

class super(SilvaElement):
    def convert(self, *args, **kwargs):
        return html.font(
            self.content.convert(*args, **kwargs),
            color='aqua'
            )

class sub(SilvaElement):
    def convert(self, *args, **kwargs):
        return html.font(
            self.content.convert(*args, **kwargs),
            color='blue'
            )

class link(SilvaElement):
    def convert(self, *args, **kwargs):
        return html.a(
            self.content.convert(*args, **kwargs),
            href=self.attrs['url']
        )

class image(SilvaElement):
    def convert(self, *args, **kwargs):
        return html.img(
            self.content.convert(*args, **kwargs),
            src=self.attrs['image_path'].content+'/image'
            )

class pre(SilvaElement):
    def compact(self):
        return self

    def convert(self, *args, **kwargs):
        return html.pre(
            self.content.convert(*args, **kwargs),
        )

class table(SilvaElement):
    def convert(self, context, *args, **kwargs):
        #context['table']=self
        t = html.table(
            self.content.convert(context, *args, **kwargs),
            self.backattr(),
            cols=self.attrs.get('columns'),
            #border=self.attrs.get('type') != 'plain' and '1' or None
            )
        #del context['table']
        return t
   
class row(SilvaElement):
    def convert(self, context, *args, **kwargs):
        return html.tr(
            self.content.convert(context, *args, **kwargs),
            #colspan = context['table'].attrs.get('columns')
        )
  
class field(SilvaElement):
    def convert(self, *args, **kwargs):
        return html.td(
            self.content.convert(*args, **kwargs)
        )


def mixin_paragraphs(container):
    """ wrap silva.p node around text"""
    content = Frag()
    breaks = 'heading','p','list','dlist','nlist','table'

    pre, tag, post = container.find_and_partition(breaks)
    if pre:
        content.append(p(*pre))
    if tag:
        content.append(tag)
    if post:
        content.extend(mixin_paragraphs(post))
    return content

""" current mapping of silva
h1  :  not in use, reserved for (future) Silva publication
       sections and custom templates
h2  :  title
h3  :  heading
h4  :  subhead
h5  :  list title
"""
