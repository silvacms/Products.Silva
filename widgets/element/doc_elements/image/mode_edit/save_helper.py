## Script (Python) "save_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# $Id: save_helper.py,v 1.13 2003/04/28 10:19:52 jw Exp $
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
node.setAttribute('path', node.input_convert(image_path))
