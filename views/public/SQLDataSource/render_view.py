## Script (Python) "render_preview"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
datasource = request.model
title = datasource.get_title_or_id()

if datasource.parameters():
    return "SQL Data Source &laquo;%s&raquo; needs parameter values to be set." % title
else:
    return context.render_data(datasource)
