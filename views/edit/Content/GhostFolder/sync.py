## Script (Python) "submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
view = context
if model.get_link_status() != model.LINK_OK:
    return view.tab_edit(message_type="error",
        message="Ghost Folder was not synchronized, because the target is "\
            "invalid.")
model.haunt()
return view.tab_edit(message_type="feedback",
    message="Ghost Folder synchronized")
