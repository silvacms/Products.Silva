## Script (Python) "redirect"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
redirect_url = context.REQUEST.node.content_url() + '/edit/tab_edit#focus'

if context.REQUEST['HTTP_USER_AGENT'].startswith('Mozilla/4.77') \
   or context.REQUEST['HTTP_USER_AGENT'].find('Konqueror') > -1 \
   or context.REQUEST['HTTP_USER_AGENT'].startswith('Opera/'):
    
    return '<html><head><META HTTP-EQUIV="refresh" CONTENT="0; URL=%s"></head><body bgcolor="#FFFFFF"></body></html>' % redirect_url

else:
    context.REQUEST.RESPONSE.redirect(redirect_url)
    return None
