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

tag = image.image.tag(css_class=alignment)

if alignment.startswith('image-'):
    # I don't want to do this... Oh well, long live CSS...
    tag = '<div class="%s">%s</div>' % (
        alignment, image.image.tag(css_class=alignment))

if link:
    tag = '<a class="image" href="%s">%s</a>' % (link, tag)

return tag
