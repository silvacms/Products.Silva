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
    image = node.restrictedTraverse(image_path)
else:
    # Backwards compatibility for image_id attribute...
    image_id = node.output_convert_html(node.getAttribute('image_id'))
    if not image_id:
        return None
    image = getattr(node.get_content().get_container(), image_id, None)

return image