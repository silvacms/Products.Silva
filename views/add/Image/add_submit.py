## Script (Python) "add_submit"
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
REQUEST = context.REQUEST

# if we cancelled, then go back to edit tab
if REQUEST.has_key('add_cancel'):
    return view.tab_edit()

# validate form
from Products.Formulator.Errors import ValidationError, FormValidationError
try:
    result = view.form.validate_all(REQUEST)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    return view.add_form(message_type="error", 
        message=view.render_form_errors(e))

id = result['object_id']
file = result['file']

# do some additional validation
if not file or not getattr(file, 'filename', None):
    return view.add_form(message_type="error", message="Empty or invalid file.")
if not id:
    id = file.filename
# if we don't have the right id, reject adding
if not model.is_id_valid(id):
  return view.add_form(message_type="error", message="%s is not a valid id." % view.quotify(id))


# try to cope with absence of title in form (happens for ghost)
if result.has_key('object_title'):
    title = model.input_convert(result['object_title'])
    del result['object_title']
else:
    title = ""

# process data in result and add using validation result
view = context

model.manage_addProduct['Silva'].manage_addImage(id, title, file=file)
object = getattr(model, id)

# update last author info in new object
object.sec_update_last_author_info()

# now go to tab_edit in case of add and edit, back to container if not.
if REQUEST.has_key('add_edit_submit'):
    REQUEST.RESPONSE.redirect(object.absolute_url() + '/edit/tab_edit')
else:
    return view.tab_edit(message_type="feedback", 
                         message="Added %s %s." % (object.meta_type, view.quotify(id)))
