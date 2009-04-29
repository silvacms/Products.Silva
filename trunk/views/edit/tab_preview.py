## Script (Python) "tab_preview"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=message_type=None,message=None
##title=
##
model = context.REQUEST.model

#send to no-frame version of preview tab if needed
if not (model.implements_container() or model.implements_content() \
        or model.implements_versioned_content() ):
    return context.tab_preview_noframes(message_type=message_type,
                                        message=message)

# if container, then send to the default documents preview tab
if model.implements_container() and model.get_default():
    model = model.get_default()

return context.tab_preview_frameset(message_type=message_type,
                                    message=message)
