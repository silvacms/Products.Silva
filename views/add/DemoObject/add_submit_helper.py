## Script (Python) "add_submit_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model, id, title, result
##title=
##
model.manage_addProduct['Silva'].manage_addDemoObject(id, title)

demoObject = getattr(model, id)

# The form is already evaluated by add_submit
# Add the data from the form as well as some default data for other fields
info = result['info']
number = 0
date = DateTime()

# now set data in version
editable = demoObject.get_editable()
editable.set_demo_data(info, number, date)

return demoObject
