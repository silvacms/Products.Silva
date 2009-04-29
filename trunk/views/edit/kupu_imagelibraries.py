## Script (Python) "kupu_imagelibraries"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml;charset=UTF-8')

root = context.get_root()
url = root.absolute_url()
path = '/'.join(root.getPhysicalPath())
icon = root.icon
title = root.get_title()

ret = """<?xml version="1.0" ?>
<libraries>
    <library id="%(id)s">
        <uri>%(url)s/kupu_imagelibrary</uri>
        <title>%(title)s</title>
        <src>%(url)s/edit/kupu_imagelibrary?path=%(path)s</src>
        <icon>%(icon)s</icon>
    </library>
</libraries>""" % {'id': path,
                    'title': title,
                    'url': url,
                    'path': path,
                    'icon': icon}

return ret
