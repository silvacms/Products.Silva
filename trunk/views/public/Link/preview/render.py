## Script (Python) "render_view"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
version = context.REQUEST.model
if context.REQUEST.get('URL','').find('tab_preview') > -1:
    # in the SMI show the public view (the redirect) in preview
    return version.redirect()
if context.REQUEST.get('URL','').find('edit') > -1:
    # when loading the preview in the edit tab of published content, 
    # render a link to the location 
    return 'Link &laquo;%s&raquo; redirects to: <a href="%s">%s</a>'%(version.get_title(),version.get_url(),version.get_url())
return version.redirect()
