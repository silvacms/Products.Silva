# $Id: save_helper.py,v 1.13.12.1 2003/10/18 12:11:57 zagy Exp $
from Products.Silva.mangle import String

request = context.REQUEST
node = request.node

image_path = request['path']
node.setAttribute('path', String.inputConvert(image_path))

link_title = request['title']
node.setAttribute('title', String.inputConvert(link_title))

link = request.get('link')
link_selector = request.get('link_selector')
if link_selector == 'hiresimg_url':
    node.setAttribute('link_to_hires', '1')
    image = context.content()
    if image:
        link = '/'.join(image_path.split('/') + ['hires_image'] )
else:
    node.setAttribute('link_to_hires', '0')
    
if link:
    node.setAttribute('link', String.inputConvert(link))
else:
    node.removeAttribute('link')

target = request.get('target')
target_selector = request.get('target_selector')
if target_selector == '_blank':
    target = '_blank'
node.setAttribute('target', target)


if request.has_key('alignment'):
    align_attribute = request['alignment']
    if align_attribute != 'none':
        node.setAttribute('alignment', String.inputConvert(align_attribute))
    else:
        node.removeAttribute('alignment')


