## Script (Python) "save_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
node = request.node

if request.has_key('alignment'):
    align_attribute = request['alignment']
    if align_attribute != 'none':
        node.setAttribute('alignment', node.input_convert(align_attribute))
    else:
        node.removeAttribute('alignment')

if request.has_key('link'):
    link = request['link']
    node.setAttribute('link', node.input_convert(link))
else:
    node.removeAttribute('link')

image_path = request['path']

# Check for non existence of a "/" - fixes traversal
# situation of Zope 2.5.1
if '/' in image_path:
    image = context.get_image(image_path)
else:
    image = getattr(node, image_path, None)

if image is not None:
    image_path = '/'.join(image.getPhysicalPath())

node.setAttribute('path', node.input_convert(image_path))
