## Script (Python) "get_all_addables"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
return [(item, item) for item in context.get_silva_addables_all()]

# This method returns a list which appears in a form (in tab_metadata).
# The entire list is a Silva 'something' (document, ghost, EUR meeting).
# Can we remove the 'Silva ' before returning?
# In the UI it's totally redundant.
