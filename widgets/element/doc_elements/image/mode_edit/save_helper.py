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
image_path = request['image_path']

if request.has_key('alignment'):
    align_attribute = request['alignment']
    if align_attribute != 'none':
        node.setAttribute('alignment', node.input_convert(align_attribute))
    else:
        node.removeAttribute('alignment')

if request.has_key('image_link'):
    link = request['image_link']
    node.setAttribute('link', node.input_convert(link))
else:
    node.removeAttribute('link')
image = context.get_image(image_path)
if image is not None:
    image_path = '/'.join(image.getPhysicalPath())
node.setAttribute('image_path', node.input_convert(image_path))

