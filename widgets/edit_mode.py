## Script (Python) "edit_mode"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
if not context.REQUEST.node.get_content().sec_create_lock():
    return context.redirect()

context.edit_mode_helper()
return context.redirect()
