## Script (Python) "tag"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

node = context.REQUEST.node
image = context.content()

if not image:
    return '<div class="error">[image reference is broken]</div>'

alignment = node.getAttribute('alignment')
link = node.getAttribute('link')
link_title = node.getAttribute('title')
target = node.getAttribute('target')

if not link_title:
    link_title = image.get_title()

tag_template = '%s'
if alignment.startswith('image-'):
    # I don't want to do this... Oh well, long live CSS...
    tag_template = '<div class="%s">%%s</div>' % alignment
tag = tag_template % image.image.tag(css_class=alignment, title=link_title)

if link:
    tag = '<a class="image" href="%s" title="%s" target="%s">%s</a>' % (
        link, link_title, target, tag)

return tag
