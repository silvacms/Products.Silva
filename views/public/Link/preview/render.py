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
if context.REQUEST.get('HTTP_REFERER','').find('tab_edit') > -1:
    # loading the preview in the SMI edit tab, so render a link to the
    # location, rather than just redirecting (which can be confusing)
    return 'Link &laquo;%s&raquo; redirects to: <a href="%s">%s</a>'%(version.get_title(),version.get_url(),version.get_url())
return version.redirect()
