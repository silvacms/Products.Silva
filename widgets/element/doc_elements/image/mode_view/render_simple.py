## Script (Python) "render_simple"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
image_path = node.output_convert_html(node.getAttribute('image_path'))
if not image_path:
    # Backwards compatibility for image_id attribute...
    image_id = node.output_convert_html(node.getAttribute('image_id'))
    if not image_id:
        return '<div class="error">[No image selected]</div>'
    image = getattr(node.get_content().get_container(), image_id, None)
else:
    image = node.restrictedTraverse(image_path)

if not image:
    return '<div class="error">[Image element broken]</div>'
return '%s' % image.view()
