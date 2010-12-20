## Script (Python) "kupu_imagelibrary"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=path
##title=
##
context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml;charset=UTF-8')

root = context.get_root()

path = path.split('/')
obj = context.restrictedTraverse(path)
uri = obj.absolute_url()
title = obj.get_title()
icon = '%s/%s' % (root.absolute_url(), obj.icon)

header = """<uri>%(uri)s</uri>
    <icon>%(icon)s</icon>
    <title>%(title)s</title>
    <description></description>
""" % {'uri': uri,
        'icon': icon,
        'title': title}

collection = """            <collection id="%(id)s">
                <uri>%(uri)s</uri>
                <title>%(title)s</title>
                <icon>%(icon)s</icon>
                <description>%(description)s</description>
                <src>%(src)s</src>
            </collection>
"""

resource = """              <resource id="%(id)s">
                <uri>%(uri)s</uri>
                <icon>%(icon)s</icon>
                <description>%(description)s</description>
                <title>%(description)s</title>
                <size>%(size)s</size>
                <preview>%(uri)s?thumbnail</preview>
            </resource>
"""

items = []
if obj != root:
    parent = obj.aq_parent
    path = '/'.join(parent.getPhysicalPath())
    data = collection % {'id': '/'.join(parent.getPhysicalPath()),
                            'title': '..',
                            'uri': parent.absolute_url(),
                            'src': '%s/kupu_imagelibrary?path=%s' % (
                                        context.absolute_url(), path),
                            'icon': '%s/%s' % (root.absolute_url(),
                                        parent.icon),
                            'description': parent.get_title()}
    items.append(data)

for indent, child in obj.get_tree(0):
    if child.implements_container():
        path = '/'.join(child.getPhysicalPath())
        data = {'id': path,
                'title': child.get_title(),
                'uri': child.absolute_url(),
                'src': '%s/kupu_imagelibrary?path=%s' % (context.absolute_url(), path),
                'icon': '%s/%s' % (root.absolute_url(), child.icon),
                'description': child.get_title()}
        items.append(collection % data)

for child in obj.get_assets():
    if child.aq_inner.meta_type == 'Silva Image':
        data = {'id': '/'.join(child.getPhysicalPath()),
                'uri': child.absolute_url(),
                'description': child.id,
                'icon': '%s/%s' % (root.absolute_url(), child.icon),
                'size': '%sx%s' % child.getDimensions(),
                }
        items.append(resource % data)

ret = """<?xml version="1.0" ?>
<collection>
%s
        <items>
%s
        </items>
</collection>
""" % (header, '\n'.join(items))

return ret
