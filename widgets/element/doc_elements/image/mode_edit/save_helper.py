## Script (Python) "save_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
image_path = context.REQUEST['image_path']

if context.REQUEST.has_key('alignment'):    
    align_attribute = context.REQUEST['alignment']
    if align_attribute != 'none':
        node.setAttribute('alignment', align_attribute)
    else:
        node.removeAttribute('alignment')

node.setAttribute('image_path', image_path)

