## Script (Python) "tab_import_action"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
xml_file = context.REQUEST['xml']
model = context.REQUEST.model
model.action_import_xml(xml_file)
return "done importing"
