## Script (Python) "render"
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

alignment = node.output_convert_editable(node.getAttribute('alignment'))
if alignment == '':    
    return image.image.tag()
elif alignment.startswith('image-'):
    # I don't want to do this... Oh well, long live CSS...
    return '<div class="%s">%s</div>' % (alignment, image.image.tag(css_class=alignment))

return image.image.tag(css_class=alignment)
