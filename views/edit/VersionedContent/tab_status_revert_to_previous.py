## Script (Python) "tab_edit_revert_to_saved"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
model.sec_update_last_author_info()
view = context
model.revert_to_previous()
#invalidate the cache
try:
    del context.REQUEST.SESSION['xmlwidgets_service_editor']
except AttributeError:
    pass
except KeyError:
    pass
return view.tab_status(message_type="feedback", message="Reverted to previous version.")
