## Script (Python) "content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.service_editor.setViewer('service_sub_previewer')
# XXX clemens hacked: add a break after a complex list element
# adds some space to the next list item (otherwise the
# end of this item may be closer to the start of the next item 
# than to the rest of this list element)
return context.service_editor.getViewer().getWidget(context.REQUEST.node).render()+ '<br />'
