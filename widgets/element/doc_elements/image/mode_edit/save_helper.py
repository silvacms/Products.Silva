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
node.setAttribute('image_path', image_path)
