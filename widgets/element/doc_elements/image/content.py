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
image_path = node.output_convert_html(node.getAttribute('path'))

return context.get_image(image_path)