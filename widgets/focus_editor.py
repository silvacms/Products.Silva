## Script (Python) "focus_editor"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=focussed_form_element=None
##title=
##
return '''
// Called from body onload() method which is defined in the
// macro_index. It focusses the appropiate form field.
function focus_editor() {
  if (document.getElementById) {
    element = document.getElementById('%s');
    if (element) element.focus();
  }
}
''' % (focussed_form_element)