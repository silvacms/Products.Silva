## Script (Python) "redirect"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
#view = context
#content_url = model.content_url() + '/edit/tab_edit'

#agent = context.REQUEST['HTTP_USER_AGENT']
#if agent.startswith('Mozilla/4.77') or agent.find('Konqueror') > -1:
#    return '<html><head><META HTTP-EQUIV="refresh" CONTENT="0; URL=%s"></head><body bgcolor="#FFFFFF"></body></html>' % content_url  
#else:
#    return context.REQUEST.RESPONSE.redirect(content_url)
return model.content_url()