##parameters=id, status_code

from Products.Silva.helpers import IdCheckValues
view = context

if status_code == IdCheckValues.ID_CONTAINS_BAD_CHARS:
    return """The id should only contain letters, digits and underscore &quot;_&quot; or a period &quot;.&quot;<br>
Additionally it should start with a letter or digit.<br>
You entered the id %s which did not match these contraints.""" % view.quotify(id)

elif status_code == IdCheckValues.ID_RESERVED_PREFIX:
    # FIXME: needs to know about the prefix
    prefix = id.split('_')[0]+'_'
    return """Ids starting with %s are reserved for internal use.<br>
Please use another id.""" % view.quotify(prefix)

elif status_code == IdCheckValues.ID_RESERVED:
    return """The id %s is reserved for internal use.<br>
Please use another id.""" % view.quotify(id)

elif status_code == IdCheckValues.ID_IN_USE_CONTENT:
    return """There is already a content with the id %s in this container.<br>
Please use another id.""" % view.quotify(id)

elif status_code == IdCheckValues.ID_IN_USE_ASSET:
    return """There is an asset with the id %s in this container.<br>
Please use another id.""" % view.quotify(id)


# this should not happen
return """(Internal Error): An invalid status %s occured while checking the id %s.<br>
Please contact the person responsible for this Silva installation or file a bug report Yourself.""" % (view.quotify(status_code), view.quotify(id))

