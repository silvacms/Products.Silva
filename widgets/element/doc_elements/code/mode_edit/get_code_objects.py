## Script (Python) "get_code_elements"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# This script returns a sorted list of available code elements for selection.
# Code elements are scripts or ZPTs residing in folders named 'code_source'.
# The script looks for such folders starting from the place of the document
# up to the Silva root.
# If a folder 'code_source' is found on the same level of the document, every
# script or ZPT contained is added to the list.
# However, scripts or ZPTs contained in 'code_source' folder above the document
# are added only if they're not hidden, i.e. if they are not member of a list
# returned by a script named 'hidden'.
# This functionality allows the site developer to selectively hide some
# code objects from being called by lower level documents.

request = context.REQUEST
model = context.REQUEST.model
obj = model.get_container()
code_objects = []
want_hiding = 0
interesting_metatypes = ['Script (Python)', 'Page Template', 'DTML Method']

while 1:
    code_source = getattr(obj.aq_explicit, 'code_source', None)
    if code_source:
        hidden = getattr(code_source.aq_explicit, 'hidden', None)
        if hidden and want_hiding:
            dont_include_ids = hidden() + ['hidden']
        else:
            dont_include_ids = ['hidden']
        code_objects.extend(
            [value for id, value in code_source.objectItems(interesting_metatypes)
             if id not in dont_include_ids])
    if obj.meta_type == 'Silva Root':
        break
    # we want hiding after the first iteration
    want_hiding = 1
    obj = obj.aq_parent

# sort by title/id
code_objects.sort(lambda x, y: cmp(x.get_title_or_id_html(), y.get_title_or_id_html()))

# return list of code objects
return code_objects
