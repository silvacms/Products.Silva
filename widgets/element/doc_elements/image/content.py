## Script (Python) "content"
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

if image_path:
    try:
        image = node.restrictedTraverse(image_path)
    except KeyError:
        # image reference is broken (i.e. renamed)
        image = None
else:
    # Backwards compatibility for image_id attribute...
    image_id = node.output_convert_html(node.getAttribute('image_id'))
    if not image_id:
        return None
    image = getattr(node.get_content().get_container(), image_id, None)

# check meta_type here ?
if image.meta_type != 'Silva Image':
    image = None

return image
